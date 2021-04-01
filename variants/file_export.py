"""This module contains the code for file export"""

import datetime
import math
from collections import OrderedDict
from datetime import timedelta
from tempfile import NamedTemporaryFile
import contextlib

from django.utils import timezone
from django.conf import settings
import vcfpy
import wrapt
import xlsxwriter

from cohorts.models import Cohort
from .models import (
    Case,
    CaseAwareProject,
    ExportFileJobResult,
    ExportProjectCasesFileBgJobResult,
    SmallVariantComment,
    annotate_with_phenotype_scores,
    annotate_with_pathogenicity_scores,
    annotate_with_joint_scores,
    prioritize_genes,
    VariantScoresFactory,
)
from .templatetags.variants_tags import flag_class
from projectroles.plugins import get_backend_api
from .queries import (
    CaseExportTableQuery,
    CaseExportVcfQuery,
    ProjectExportTableQuery,
    ProjectExportVcfQuery,
)
from variants.helpers import SQLALCHEMY_ENGINE

#: Color to use for variants flagged as positive.
BG_COLOR_POSITIVE = "#dc3848"

#: Color to use for variants flagged as uncertain.
BG_COLOR_UNCERTAIN = "#ffc105"

#: Color to use for variants flagged as negative.
BG_COLOR_NEGATIVE = "#29a847"

#: Map of flag value to color.
BG_COLORS = {
    "positive": BG_COLOR_POSITIVE,
    "uncertain": BG_COLOR_UNCERTAIN,
    "negative": BG_COLOR_NEGATIVE,
}


#: Constant that determines how many days generated files should stay.  Note for the actual removal, a separate
#: Celery job must be ran.
EXPIRY_DAYS = 14


def to_str(val):
    if val is None:
        return "."
    elif isinstance(val, set):
        return ";".join(sorted(map(to_str, val)))
    elif isinstance(val, list):
        return ";".join(map(to_str, val))
    else:
        return str(val)


#: Names of the fixed header columns: ``(id/name, title, type)``.
HEADER_FIXED = (
    ("chromosome", "Chromosome", str),
    ("start", "Position", int),
    ("reference", "Reference bases", str),
    ("alternative", "Alternative bases", str),
    ("var_type", "Variant types", list),
    ("rsid", "dbSNP ID", str),
    ("in_clinvar", "In Clinvar?", bool),
    ("exac_frequency", "Max. freq. in ExAC", float),
    ("gnomad_exomes_frequency", "Max. freq. in gnomAD exomes", float),
    ("gnomad_genomes_frequency", "Max. freq. in gnomAD gnomes", float),
    ("thousand_genomes_frequency", "Freq. in thousand genomes", float),
    ("inhouse_carriers", "Carriers in in-house DB", int),
    ("exac_homozygous", "Homozygous counts in ExAC", int),
    ("gnomad_exomes_homozygous", "Homozygous counts in gnomAD exomes", int),
    ("gnomad_genomes_homozygous", "Homozygous counts in gnomAD genomes", int),
    ("thousand_genomes_homozygous", "Homozygous counts in Thousand Genomes", int),
    ("inhouse_hom_alt", "Homozygous counts in in-house DB", int),
    ("exac_heterozygous", "Heterozygous counts in ExAC", int),
    ("gnomad_exomes_heterozygous", "Heterozygous counts in gnomAD exomes", int),
    ("gnomad_genomes_heterozygous", "Heterozygous counts in gnomAD genomes", int),
    ("thousand_genomes_heterozygous", "Heterozygous counts in Thousand Genomes", int),
    ("inhouse_het", "Heterozygous counts in in-house DB", int),
    ("symbol", "Gene Symbol", str),
    ("gene_id", "Gene ID", str),
    ("effect", "Most pathogenic variant effect", str),
    ("hgvs_p", "Protein HGVS change", str),
    ("hgvs_c", "Nucleotide HGVS change", str),
    ("known_gene_aa", "100 Vertebrate AA conservation", str),
    ("gene_name", "Gene Name", str),
    ("gene_family", "Gene Family", str),
    ("pubmed_id", "Gene Pubmed ID", str),
)
if settings.KIOSK_MODE:
    HEADER_FIXED = tuple(filter(lambda x: not x[0].startswith("inhouse_"), HEADER_FIXED))

#: Names of the phenotype-scoring header columns.
HEADERS_PHENO_SCORES = (
    ("phenotype_score", "Phenotype Score", float),
    ("phenotype_rank", "Phenotype Rank", int),
)

#: Names of the pathogenicity scoring header columns.
HEADERS_PATHO_SCORES = (
    ("pathogenicity_score", "Pathogenicity Score", float),
    ("pathogenicity_rank", "Pathogenicity Rank", int),
)

#: Names of the joint scoring header columns.
HEADERS_JOINT_SCORES = (
    ("joint_score", "Pheno+Patho Score", float),
    ("joint_rank", "Pheno+Patho Rank", int),
)

#: Header fields for flags.
HEADER_FLAGS = (
    ("flag_bookmarked", "Flag: bookmarked", str),
    ("flag_candidate", "Flag: selected as candidate disease-causing", str),
    ("flag_final_causative", "Flag: selected as final causative variant", str),
    ("flag_for_validation", "Flag: selected for validation", str),
    ("flag_molecular", "Rating: variant is molecular", str),
    ("flag_visual", "Rating: visual inspection of alignment", str),
    ("flag_validation", "Rating: validation result", str),
    ("flag_phenotype_match", "Rating: clinic/phenotype/biology", str),
    ("flag_summary", "Rating: manual summary", str),
)

#: Header fields for comments.
HEADER_COMMENTS = (("comment_count", "Comment count", int),)

#: Per-sample headers.
HEADER_FORMAT = (
    ("gt", "Genotype", str),
    ("gq", "Gt. Quality", str),
    ("ad", "Alternative depth", int),
    ("dp", "Total depth", int),
    ("aaf", "Alternate allele fraction", float),
)

#: Contig lenghts for GRCh37
CONTIGS_GRCH37 = (
    ("1", 249250621),
    ("2", 243199373),
    ("3", 198022430),
    ("4", 191154276),
    ("5", 180915260),
    ("6", 171115067),
    ("7", 159138663),
    ("8", 146364022),
    ("9", 141213431),
    ("10", 135534747),
    ("11", 135006516),
    ("12", 133851895),
    ("13", 115169878),
    ("14", 107349540),
    ("15", 102531392),
    ("16", 90354753),
    ("17", 81195210),
    ("18", 78077248),
    ("19", 59128983),
    ("20", 63025520),
    ("21", 48129895),
    ("22", 51304566),
    ("X", 155270560),
    ("Y", 59373566),
    ("MT", 16569),
)


class RowWithSampleProxy(wrapt.ObjectProxy):
    """Allow setting sample name into a result row."""

    def __init__(self, wrapped, sample_name):
        super().__init__(wrapped)
        self._self_sample_name = sample_name

    @property
    def sample_name(self):
        return self._self_sample_name

    @property
    def genotype(self):
        patch = {"sample": self.__wrapped__.genotype[self.sample_name]}
        return {**self.__wrapped__.genotype, **patch}

    def __getitem__(self, key):
        if key == "sample_name":
            return self._self_sample_name
        elif key == "genotype":
            return self.genotype
        else:
            return self.__wrapped__.__getitem__(key)


class RowWithJoinProxy(wrapt.ObjectProxy):
    """Allow setting sample name into a result row."""

    def __init__(self, wrapped):
        super().__init__(wrapped)
        self._self_genotypes_to_join = dict()

    def add_genotype(self, genotype):
        self._self_genotypes_to_join.update(genotype)

    @property
    def genotype(self):
        return {**self.__wrapped__.genotype, **self._self_genotypes_to_join}

    def __getitem__(self, key):
        if key == "genotype":
            return self.genotype
        return self.__wrapped__.__getitem__(key)


class CaseExporterBase:
    """Base class for export of (filtered) case data from single case or all cases of a project.
    """

    #: The query class to use for building single-case queries.
    query_class_single_case = None
    #: The query class to use for building project-wide queries.
    query_class_project_cases = None

    def __init__(self, job, case_or_project_or_cohort):
        #: The ``ExportFileBgJob``, ``CADDSubmissionBgJob``, or ``DistillerSubmissionBgJob`` to use for logging.
        #: Variants are obtained from ``case_or_project``.
        self.job = job
        #: The case to export for, if any.
        self.case = None
        #: The project to export for, if any.
        self.project_or_cohort = None
        if isinstance(case_or_project_or_cohort, Case):
            self.case = case_or_project_or_cohort
        else:
            self.project_or_cohort = case_or_project_or_cohort
        #: The SQL Alchemy connection to use.
        self._alchemy_engine = None
        #: The query arguments.
        self.query_args = job.query_args
        #: The named temporary file object to use for file handling.
        self.tmp_file = None
        #: The wrapper for running queries.
        self.query = None
        if self.project_or_cohort:
            self.query = self.query_class_project_cases(
                self.project_or_cohort, self.get_alchemy_engine(), user=job.bg_job.user
            )
        else:
            self.query = self.query_class_single_case(self.case, self.get_alchemy_engine())
        #: The name of the selected members.
        self.members = self._get_members_sorted()
        #: The column information.
        self.columns = list(self._yield_columns(self.members))

    def get_alchemy_engine(self):
        if not self._alchemy_engine:
            self._alchemy_engine = SQLALCHEMY_ENGINE
        return self._alchemy_engine

    def _is_prioritization_enabled(self):
        """Return whether prioritization is enabled in this query."""
        return settings.VARFISH_ENABLE_EXOMISER_PRIORITISER and all(
            (
                self.query_args.get("prio_enabled"),
                self.query_args.get("prio_algorithm"),
                self.query_args.get("prio_hpo_terms", []),
            )
        )

    def _is_pathogenicity_enabled(self):
        """Return whether pathogenicity scoring is enabled in this query."""
        return settings.VARFISH_ENABLE_CADD and all(
            (self.query_args.get("patho_enabled"), self.query_args.get("patho_score"))
        )

    def _get_members_sorted(self):
        """Get list of selected members."""
        members = []
        if self.project_or_cohort:
            members.append("sample")
        else:
            for m in self.job.case.get_filtered_pedigree_with_samples():
                if self.query_args.get("%s_export" % m["patient"], False):
                    members.append(m["patient"])
        return sorted(members)

    def _yield_columns(self, members):
        """Yield column information."""
        if self.project_or_cohort:
            header = [("sample_name", "Sample", str)]
        else:
            header = []
        header += HEADER_FIXED
        if self._is_prioritization_enabled():
            header += HEADERS_PHENO_SCORES
        if self._is_pathogenicity_enabled():
            header += HEADERS_PATHO_SCORES
        if self._is_prioritization_enabled() and self._is_pathogenicity_enabled():
            header += HEADERS_JOINT_SCORES
        if self.query_args["export_flags"]:
            header += HEADER_FLAGS
        if self.query_args["export_comments"]:
            header += HEADER_COMMENTS
        for lst in header:
            yield dict(zip(("name", "title", "type", "fixed"), list(lst) + [True]))
        for member in members:
            for name, title, type_ in HEADER_FORMAT:
                yield {
                    "name": "%s.%s" % (member, name),
                    "title": "%s %s" % (member, title),
                    "type": type_,
                    "fixed": False,
                }

    def _yield_smallvars(self):
        """Use this for yielding the resulting small variants one-by-one."""
        prev_chrom = None
        self.job.add_log_entry("Executing database query...")
        with contextlib.closing(self.query.run(self.query_args)) as result:
            self.job.add_log_entry("Executing phenotype score query...")
            _result = list(result)
            if self._is_prioritization_enabled():
                gene_scores = self._fetch_gene_scores([entry.entrez_id for entry in _result])
                _result = annotate_with_phenotype_scores(_result, gene_scores)
            if self._is_pathogenicity_enabled():
                variant_scores = self._fetch_variant_scores(
                    [
                        (
                            entry["chromosome"],
                            entry["start"],
                            entry["reference"],
                            entry["alternative"],
                        )
                        for entry in _result
                    ]
                )
                _result = annotate_with_pathogenicity_scores(_result, variant_scores)
            if self._is_prioritization_enabled() and self._is_pathogenicity_enabled():
                _result = annotate_with_joint_scores(_result)
            self.job.add_log_entry("Writing output file...")
            total = len(_result)
            steps = math.ceil(total / 10)
            for i, small_var in enumerate(_result):
                if self._is_prioritization_enabled() or self._is_pathogenicity_enabled():
                    if i % steps == 0:
                        self.job.add_log_entry("{}%".format(int(100 * i / total)))
                else:
                    if small_var.chromosome != prev_chrom:
                        self.job.add_log_entry(
                            "Now on chromosome chr{} ({}%)".format(
                                small_var.chromosome, int(100 * i / total)
                            )
                        )
                    prev_chrom = small_var.chromosome
                if self.project_or_cohort:
                    for sample in sorted(small_var.genotype.keys()):
                        if self.query_class_project_cases is ProjectExportVcfQuery:
                            yield RowWithJoinProxy(small_var)
                        else:
                            yield RowWithSampleProxy(small_var, sample)
                else:
                    yield small_var

    def _fetch_gene_scores(self, entrez_ids):
        if self._is_prioritization_enabled():
            try:
                prio_algorithm = self.query_args.get("prio_algorithm")
                hpo_terms = tuple(sorted(self.query_args.get("prio_hpo_terms_curated", [])))
                return {
                    str(gene_id): score
                    for gene_id, _, score, _ in prioritize_genes(
                        entrez_ids, hpo_terms, prio_algorithm
                    )
                }
            except ConnectionError as e:
                self.job.add_log_entry(e)
        else:
            return {}

    def _fetch_variant_scores(self, variants):
        if self._is_pathogenicity_enabled():
            try:
                patho_score = self.query_args.get("patho_score")
                scorer_factory = VariantScoresFactory()
                scorer = scorer_factory.get_scorer(patho_score, variants, self.job.bg_job.user)
                return {
                    "-".join(
                        [
                            score["release"],
                            score["chromosome"],
                            str(score["start"]),
                            score["reference"],
                            score["alternative"],
                        ]
                    ): (score["score"], score["info"])
                    for score in scorer.score()
                }
            except ConnectionError as e:
                self.job.add_log_entry(e)
        else:
            return {}

    def _get_named_temporary_file_args(self):
        return {}

    def __enter__(self):
        self.tmp_file = NamedTemporaryFile(**self._get_named_temporary_file_args())
        self.tmp_file.__enter__()
        self._open()
        return self

    def __exit__(self, exc, value, tb):
        result = self.tmp_file.__exit__(exc, value, tb)
        self._close()
        self.tmp_file = None
        return result

    def generate(self):
        """Perform data generation and return all data."""
        return self.write_tmp_file().read()

    def write_tmp_file(self):
        """Write generated data to temporary file and return file-like object for reading data from."""
        self._write_leading()
        self._write_variants()
        self._write_trailing()
        #: Rewind temporary file to beginning and return it.
        self.tmp_file.flush()
        self.tmp_file.seek(0)
        return self.tmp_file

    def _open(self):
        """Override with action on opening the file."""

    def _close(self):
        """Override with action on closing the file."""

    def _write_leading(self):
        """Write out anything before the the per-variant data.

        Override in sub class.
        """

    def _write_variants(self):
        """Write out the actual data, override called functions rather than this one.
        """
        self._begin_write_variants()
        self._write_variants_header()
        self._write_variants_data()
        self._end_write_variants()

    def _begin_write_variants(self):
        """Fill with actions to execute before writing variants."""

    def _write_variants_header(self):
        """Fill with actions to write the variant header."""

    def _write_variants_data(self):
        """Fill with actions to write the variant data."""

    def _end_write_variants(self):
        """Fill with actions to execute after writing variants."""

    def _write_trailing(self):
        """Write out anything after the per-variant data.

        Override in sub class.
        """


class CaseExporterTsv(CaseExporterBase):
    """Export a case to TSV format."""

    query_class_single_case = CaseExportTableQuery
    query_class_project_cases = ProjectExportTableQuery

    def _write_variants_header(self):
        """Fill with actions to write the variant header."""
        line = "\t".join([x["title"] for x in self.columns]) + "\n"
        self.tmp_file.write(line.encode("utf-8"))

    def _write_variants_data(self):
        """Fill with actions to write the variant data."""
        for small_var in self._yield_smallvars():
            row = []
            for column in self.columns:
                if column["name"] == "chromosome":
                    row.append("chr" + getattr(small_var, "chromosome"))
                elif column["fixed"]:
                    row.append(getattr(small_var, column["name"]))
                else:
                    member, field = column["name"].rsplit(".", 1)
                    if field == "aaf":
                        ad = small_var.genotype.get(member, {}).get("ad", 0)
                        dp = small_var.genotype.get(member, {}).get("dp", 0)
                        aaf = ad / dp if dp != 0 else 0
                        row.append(str(aaf))
                    else:
                        row.append(small_var.genotype.get(member, {}).get(field, "."))
            line = "\t".join(map(lambda s: to_str(s), row)) + "\n"
            self.tmp_file.write(line.encode("utf-8"))


class CaseExporterXlsx(CaseExporterBase):
    """Export a case to Excel (XLSX) format."""

    query_class_single_case = CaseExportTableQuery
    query_class_project_cases = ProjectExportTableQuery

    def __init__(self, job, case_or_project_or_cohort):
        super().__init__(job, case_or_project_or_cohort)
        #: The ``Workbook`` object to use for writing.
        self.workbook = None
        #: The sheet with the variants.
        self.variant_sheet = None
        #: The sheet with the meta data.
        self.meta_data_sheet = None
        #: The sheet with comments
        self.comment_sheet = None

    def _get_named_temporary_file_args(self):
        return {"suffix": ".xlsx"}

    def _open(self):
        self.workbook = xlsxwriter.Workbook(self.tmp_file.name, {"remove_timezone": True})
        # setup formats
        self.header_format = self.workbook.add_format({"bold": True})
        # setup sheets
        self.variant_sheet = self.workbook.add_worksheet("Variants")
        if self.query_args["export_comments"]:
            self.comment_sheet = self.workbook.add_worksheet("Comments")
        self.meta_data_sheet = self.workbook.add_worksheet("Metadata")
        # setup styles
        self.styles = {}
        for name, color in BG_COLORS.items():
            self.styles[name] = self.workbook.add_format({"bg_color": color})

    def _end_write_variants(self):
        self.workbook.close()

    @staticmethod
    def _unblank(x):
        if x is None:
            return "None"
        elif x is True:
            return "True"
        elif x is False:
            return "False"
        elif isinstance(x, str) and not x:
            return "."
        else:
            return x

    def _write_leading(self):
        if self.query_args["export_comments"]:
            self._write_comment_sheet()
        self._write_metadata_sheet()

    def _write_comment_sheet(self):
        # Write out meta data sheet.
        if self.project_or_cohort:
            header_prefix = ["Case"]
        else:
            header_prefix = []
        self.comment_sheet.write_row(
            0,
            0,
            header_prefix
            + ["Chromosome", "Position", "Reference", "Alternative", "Date", "Author", "Comment"],
            self.header_format,
        )
        if self.case:
            cases = [self.case]
        else:
            if isinstance(self.project_or_cohort, Cohort):
                cases = [
                    case
                    for case in self.project_or_cohort.get_accessible_cases_for_user(
                        self.job.bg_job.user
                    )
                ]
            else:  # project
                cases = [case for case in self.project_or_cohort.case_set.all()]
        offset = 1
        for case in cases:
            for comment in SmallVariantComment.objects.filter(case=case):
                row = [
                    comment.chromosome,
                    comment.start,
                    comment.end,
                    comment.bin,
                    comment.reference,
                    comment.alternative,
                    comment.date_created,
                    comment.user.username,
                    comment.text,
                ]
                if self.project_or_cohort:
                    row.insert(0, case.name)
                self.variant_sheet.write_row(offset, 0, row)
                offset += 1

    def _write_metadata_sheet(self):
        # Write out meta data sheet.
        self.meta_data_sheet.write_column(
            0,
            0,
            ["Case", "", "Date", "", "Versions", "", "Settings"] + list(self.query_args.keys()),
            self.header_format,
        )
        self.meta_data_sheet.write_column(
            0,
            1,
            [
                "TODO: URL to case",
                "",
                str(datetime.datetime.now()),
                "",
                "TODO: Write out software and all database versions etc." "",
                "",
                "",
            ]
            + list(map(self.__class__._unblank, map(str, self.query_args.values()))),
        )

    def _write_variants_header(self):
        """Fill with actions to write the variant header."""
        self.variant_sheet.write_row(0, 0, [x["title"] for x in self.columns], self.header_format)

    def _write_variants_data(self):
        """Fill with actions to write the variant data."""
        # Write data to Excel sheet
        num_rows = 0
        for num_rows, small_var in enumerate(self._yield_smallvars()):
            row = []
            for column in self.columns:
                if column["name"] == "chromosome":
                    row.append("chr" + getattr(small_var, "chromosome"))
                elif column["fixed"]:
                    row.append(small_var[column["name"]])
                else:
                    member, field = column["name"].rsplit(".", 1)
                    if field == "aaf":
                        ad = small_var["genotype"].get(member, {}).get("ad", 0)
                        dp = small_var["genotype"].get(member, {}).get("dp", 0)
                        aaf = ad / dp if dp != 0 else 0.0
                        row.append(aaf)
                    else:
                        row.append(small_var["genotype"].get(member, {}).get(field, "."))
                if isinstance(row[-1], list):
                    row[-1] = to_str(row[-1])
            fmt = (
                self.styles.get(flag_class(small_var)) if self.query_args["export_flags"] else None
            )
            self.variant_sheet.write_row(1 + num_rows, 0, list(map(str, row)), fmt)
        # Freeze first row and first four columns and setup auto-filter.
        self.variant_sheet.freeze_panes(1, 4)
        self.variant_sheet.autofilter(0, 0, num_rows + 1, len(self.columns))


class CaseExporterVcf(CaseExporterBase):
    """Export a case to VCF format."""

    query_class_single_case = CaseExportVcfQuery
    query_class_project_cases = ProjectExportVcfQuery

    def __init__(self, job, case_or_project_or_cohort, members=None):
        super().__init__(job, case_or_project_or_cohort)
        #: The ``vcfpy.Writer`` to use for writing the VCF file.
        self.vcf_writer = None
        #: Make overriding member possible here, e.g., to upload only variants without genotypes.
        self.members = members or self.members

    def _get_named_temporary_file_args(self):
        return {"suffix": ".vcf.gz"}

    def _open(self):
        # Setup header
        lines = [
            vcfpy.HeaderLine("fileformat", "VCFv4.2"),
            vcfpy.FormatHeaderLine.from_mapping(
                {
                    "ID": "AD",
                    "Number": "R",
                    "Type": "Integer",
                    "Description": "Allelic depths for the ref and alt alleles in the order listed",
                }
            ),
            vcfpy.FormatHeaderLine.from_mapping(
                {
                    "ID": "DP",
                    "Number": "1",
                    "Type": "Integer",
                    "Description": "Approximate read depth at the locus",
                }
            ),
            vcfpy.FormatHeaderLine.from_mapping(
                {
                    "ID": "GQ",
                    "Number": "1",
                    "Type": "Integer",
                    "Description": "Phred-scaled genotype quality",
                }
            ),
            vcfpy.FormatHeaderLine.from_mapping(
                {"ID": "GT", "Number": "1", "Type": "String", "Description": "Genotype"}
            ),
        ]
        # Add header lines for contigs.
        # TODO: switch based on release in case
        for name, length in CONTIGS_GRCH37:
            lines.append(vcfpy.ContigHeaderLine.from_mapping({"ID": name, "length": length}))
        header = vcfpy.Header(lines=lines, samples=vcfpy.SamplesInfos(self.members))
        # Open VCF writer
        self.vcf_writer = vcfpy.Writer.from_path(self.tmp_file.name, header)

    def _end_write_variants(self):
        self.vcf_writer.close()

    def _yield_smallvars(self):
        if self.case:
            yield from super()._yield_smallvars()
        else:
            joined_variants = OrderedDict()
            for i in super()._yield_smallvars():
                key = (i.release, i.chromosome, i.start, i.end, i.reference, i.alternative)
                if key in joined_variants:
                    joined_variants[key].add_genotype(i.genotype)
                else:
                    joined_variants[key] = i
            for key, value in joined_variants.items():
                yield value

    def _write_variants_data(self):
        for small_var in self._yield_smallvars():
            # Get variant type
            if len(small_var.reference) == 1 and len(small_var.alternative) == 1:
                var_type = vcfpy.SNV
            elif len(small_var.reference) == len(small_var.alternative):
                var_type = vcfpy.MNV
            else:
                var_type = vcfpy.INDEL
            # Build list of calls
            calls = [
                vcfpy.Call(
                    member,
                    {
                        key.upper(): f(small_var.genotype.get(member, {}).get(key, default_value))
                        for key, default_value, f in (
                            ("gt", "./.", lambda x: x),
                            ("gq", None, lambda x: x),
                            ("ad", None, lambda x: None if x is None else [x]),
                            ("dp", None, lambda x: x),
                        )
                    },
                )
                for member in self.members
            ]
            # Construct and write out the VCF ``Record`` object
            self.vcf_writer.write_record(
                vcfpy.Record(
                    small_var.chromosome,
                    small_var.start,
                    [],
                    small_var.reference,
                    [vcfpy.Substitution(var_type, small_var.alternative)],
                    None,
                    [],
                    {},
                    ["GT", "GQ", "AD", "DP"],
                    calls,
                )
            )

    def _get_members_sorted(self):
        """Get list of selected members."""
        members = []
        if self.project_or_cohort:
            for m in self.project_or_cohort.get_filtered_pedigree_with_samples(
                self.job.bg_job.user
            ):
                members.append(m["patient"])
        else:
            for m in self.job.case.get_filtered_pedigree_with_samples():
                if self.query_args.get("%s_export" % m["patient"], False):
                    members.append(m["patient"])
        return sorted(members)


#: Dict mapping file type to writer class.
EXPORTERS = {"tsv": CaseExporterTsv, "vcf": CaseExporterVcf, "xlsx": CaseExporterXlsx}


def export_case(job):
    """Export a ``Case`` object, store result in a new ``ExportFileJobResult``."""
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="case_export",
            description="export filtration results for case {case_name}",
            status_type="INIT",
        )
        tl_event.add_object(obj=job.case, label="case_name", name=job.case.name)
    try:
        klass = EXPORTERS[job.file_type]
        with klass(job, job.case) as exporter:
            ExportFileJobResult.objects.create(
                job=job,
                expiry_time=timezone.now() + timedelta(days=EXPIRY_DAYS),
                payload=exporter.generate(),
            )
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "export failed for {case_name}")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "export complete for {case_name}")


def clear_expired_exported_files():
    """Clear expired exported files."""
    ExportFileJobResult.objects.filter(expiry_time__lt=timezone.now()).delete()
    ExportProjectCasesFileBgJobResult.objects.filter(expiry_time__lt=timezone.now()).delete()


def export_project_cases(job):
    """Export a ``Case`` object, store result in a new ``ExportProjectCasesFileBgJobResult``."""
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="project_cases_export",
            description="export filtration results for all cases in project",
            status_type="INIT",
        )
    try:
        klass = EXPORTERS[job.file_type]
        project_or_cohort = job.cohort or CaseAwareProject.objects.get(pk=job.project.pk)
        with klass(job, project_or_cohort) as exporter:
            ExportProjectCasesFileBgJobResult.objects.create(
                job=job,
                expiry_time=timezone.now() + timedelta(days=EXPIRY_DAYS),
                payload=exporter.generate(),
            )
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "export failed for all cases in project")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "export complete for all case in project")
