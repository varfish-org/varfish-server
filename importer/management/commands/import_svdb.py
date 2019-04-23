"""Import of a database of structural variants for the ``svdbs`` app.
"""

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"

import gzip
import os

import binning
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError
from django.utils import timezone
import vcfpy

from ...models import ImportInfo
from svdbs.models import (
    DgvGoldStandardSvs,
    DgvSvs,
    ExacCnv,
    EXAC_SV_TYPE_DELETION,
    EXAC_SV_TYPE_DUPLICATION,
    ThousandGenomesSv,
    DbVarSv,
    GnomAdSv,
)

#: Headers used in GFF3.
GFF3_HEADERS = ("seqid", "source", "type", "start", "end", "score", "strand", "phase", "attributes")


class DgvGoldStandardImporter:
    """Class for the import of the DGV SV GFF3 file."""

    def __init__(self, stdout, style, path, name, database):
        #: Output stream
        self.stdout = stdout
        #: Style...
        self.style = style
        #: Path to file to import.
        self.path = path
        #: Name of the database stored in the file.
        self.name = name
        if name != "dgv-gs-GRCh37":
            raise CommandError("Invalid database name {}".format(name))
        #: DB configuration
        self.database = database
        #: The genome release to import for
        self.genome_release = "GRCh37"
        #: Seen IDs to prevent duplicate import
        self.seen_ids = set()

    def clear_db(self):
        self.stdout.write("Removing old entries...")
        DgvGoldStandardSvs.objects.filter(release=self.genome_release).delete()
        self.stdout.write(self.style.SUCCESS("Successfully removed old entries"))

    def perform_import(self):
        self.clear_db()
        self.stdout.write("Importing DGV gold standard file {}".format(self.path))
        with open(self.path, "rt") as inputf:
            chrom = None
            # Read file and insert into database.
            for line in inputf:
                if line:
                    line = line[:-1]
                if not line:
                    continue  # skip empty lines
                arr = line.split("\t")
                if len(arr) != len(GFF3_HEADERS):
                    raise CommandError(
                        "Too few entries (%d vs %d) in line %s"
                        % (len(arr), len(GFF3_HEADERS), repr(line))
                    )
                values = dict(zip(GFF3_HEADERS, arr))
                values["attributes"] = {
                    key: value
                    for key, value in [
                        entry.split("=", 1) for entry in values["attributes"].split(";")
                    ]
                }
                if values["attributes"]["ID"] in self.seen_ids:
                    continue
                else:
                    self.seen_ids.add(values["attributes"]["ID"])
                if values["seqid"].startswith("chr"):
                    values["seqid"] = values["seqid"][3:]
                self.perform_insert(values)
                # read next line
                if chrom != values["seqid"]:
                    self.stdout.write("Starting contig {}".format(values["seqid"]))
                chrom = values["seqid"]
        self.stdout.write(self.style.SUCCESS("Done importing DGV gold standard file"))

    def perform_insert(self, values):
        """Insert record into database."""
        attributes = values["attributes"]
        pop_sum = {
            key: value
            for key, value in [x.split(" ") for x in attributes["PopulationSummary"].split(":")]
        }

        DgvGoldStandardSvs.objects.create(
            release=self.genome_release,
            chromosome=values["seqid"],
            start_outer=attributes["outer_start"],
            start_inner=attributes["inner_start"],
            end_inner=attributes["inner_end"],
            end_outer=attributes["outer_end"],
            bin=binning.assign_bin(
                int(attributes["outer_start"]) - 1, int(attributes["outer_end"])
            ),
            containing_bins=binning.containing_bins(
                int(attributes["outer_start"]) - 1, int(attributes["outer_end"])
            ),
            accession=attributes["ID"],
            sv_type=attributes["variant_type"],
            sv_sub_type=attributes["variant_sub_type"],
            num_studies=attributes["num_studies"],
            studies=attributes["Studies"].split(","),
            num_platforms=attributes["num_platforms"],
            platforms=attributes["Platforms"].split(","),
            num_algorithms=attributes["number_of_algorithms"],
            algorithms=attributes["algorithms"].split(","),
            num_variants=attributes["num_variants"],
            num_carriers=attributes["num_samples"],
            num_unique_samples=attributes["num_unique_samples_tested"],
            num_carriers_african=pop_sum["African"],
            num_carriers_asian=pop_sum["Asian"],
            num_carriers_european=pop_sum["European"],
            num_carriers_mexican=pop_sum["Mexican"],
            num_carriers_middle_east=pop_sum["MiddleEast"],
            num_carriers_native_american=pop_sum["NativeAmerican"],
            num_carriers_north_american=pop_sum["NorthAmerican"],
            num_carriers_oceania=pop_sum["Oceania"],
            num_carriers_south_american=pop_sum["SouthAmerican"],
            num_carriers_admixed=pop_sum["Admixed"],
            num_carriers_unknown=pop_sum["Unknown"],
        )


class DgvImporter:
    """Class for the import of DGV text files."""

    def __init__(self, stdout, style, path, name, database):
        #: Output stream
        self.stdout = stdout
        #: Style...
        self.style = style
        #: Path to file to import.
        self.path = path
        #: Name of the database stored in the file.
        self.name = name
        if name not in ("dgv-GRCh37", "dgv-GRCh38"):
            raise CommandError("Invalid database name {}".format(name))
        #: DB configuration
        self.database = database
        #: The genome release to import for
        self.genome_release = self.name.split("-")[-1]

    def clear_db(self):
        self.stdout.write("Removing old entries...")
        DbVarSv.objects.filter(release=self.genome_release).delete()
        self.stdout.write(self.style.SUCCESS("Successfully removed old entries"))

    def perform_import(self):
        self.clear_db()
        self.stdout.write("Importing DGV file {}".format(self.path))
        with open(self.path, "rt") as inputf:
            chrom = None
            header = inputf.readline()[:-1].split("\t")
            # Read file and insert into database.
            buffer = inputf.readline()
            while buffer:
                if buffer:
                    buffer = buffer[:-1]
                if not buffer:
                    continue  # skip empty lines
                arr = buffer.split("\t")
                if len(arr) != len(header):
                    raise CommandError(
                        "Too few entries (%d vs %d) in line %s"
                        % (len(header), len(arr), repr(buffer))
                    )
                values = dict(zip(header, arr))
                self.perform_insert(values)
                # read next line
                if chrom != values["chr"]:
                    self.stdout.write("Starting contig {}".format(values["chr"]))
                chrom = values["chr"]
                buffer = inputf.readline()
        self.stdout.write(self.style.SUCCESS("Done importing DGV file"))

    def perform_insert(self, values):
        """Insert record into database."""
        DgvSvs.objects.create(
            release=self.genome_release,
            chromosome=values["chr"],
            start=values["start"],
            end=values["end"],
            bin=binning.assign_bin(int(values["start"]) - 1, int(values["end"])),
            containing_bins=binning.containing_bins(int(values["start"]) - 1, int(values["end"])),
            accession=values["variantaccession"],
            sv_type=values["varianttype"],
            sv_sub_type=values["variantsubtype"],
            study=values["reference"],
            platform=values["platform"].split(","),
            num_samples=values["samplesize"] or 0,
            observed_gains=values["observedgains"] or 0,
            observed_losses=values["observedlosses"] or 0,
        )


class ExacCnvImporter:
    """Class for the import of ExAC CNV files."""

    def __init__(self, stdout, style, path, name, database):
        #: Output stream
        self.stdout = stdout
        #: Style...
        self.style = style
        #: Path to file to import.
        self.path = path
        #: Name of the database stored in the file.
        self.name = name
        if name != "exac-GRCh37":
            raise CommandError("Invalid database name {}".format(name))
        #: DB configuration
        self.database = database
        #: The genome release to import for
        self.genome_release = self.name.split("-")[1]

    def clear_db(self):
        self.stdout.write("Removing old entries...")
        ExacCnv.objects.filter(release=self.genome_release).delete()
        self.stdout.write(self.style.SUCCESS("Successfully removed old entries"))

    def perform_import(self):
        self.clear_db()
        self.stdout.write("Importing ExAC CNV file {}".format(self.path))
        with open(self.path, "rt") as inputf:
            chrom = None
            var_type = None
            for line in inputf:
                if line and line[-1] == "\n":
                    line = line[:-1]
                if line.startswith("track"):
                    if line.split()[1].startswith("name=delControls"):
                        var_type = EXAC_SV_TYPE_DELETION
                    else:
                        if not line.split()[1].startswith("name=dupControls"):
                            raise CommandError("Unexpected track line: {}".format(line))
                        var_type = EXAC_SV_TYPE_DUPLICATION
                else:
                    arr = line.split()
                    ExacCnv.objects.create(
                        release=self.genome_release,
                        chromosome=arr[0][len("chr") :],
                        start=arr[1],
                        end=arr[2],
                        bin=binning.assign_bin(int(arr[1]) - 1, int(arr[2])),
                        containing_bins=binning.containing_bins(int(arr[1]) - 1, int(arr[2])),
                        sv_type=var_type,
                        population=arr[3].split("-")[1],
                        phred_score=arr[4],
                    )
                    # read next line
                    if chrom != arr[0]:
                        self.stdout.write(
                            "Starting sv type {} on contig {}".format(var_type, arr[0])
                        )
                    chrom = arr[0]


class ThousandGenomesImporter:
    """Class for the import of thousand genomes SVs."""

    def __init__(self, stdout, style, path, name, panel_path, database):
        #: Output stream
        self.stdout = stdout
        #: Style...
        self.style = style
        #: Path to file to import.
        self.path = path
        #: Name of the database stored in the file.
        self.name = name
        if name != "thousand-genomes-svs-GRCh37":
            raise CommandError("Invalid database name {}".format(name))
        #: DB configuration
        self.database = database
        #: The genome release to import for
        self.genome_release = self.name.split("-")[-1]
        #: Path to panel mapping
        self.panel_path = panel_path

    def clear_db(self):
        self.stdout.write("Removing old entries...")
        ThousandGenomesSv.objects.filter(release=self.genome_release).delete()
        self.stdout.write(self.style.SUCCESS("Successfully removed old entries"))

    def perform_import(self):
        self.clear_db()
        self.stdout.write("Loading panel map...")
        panel_map = self.load_panel_map()
        self.stdout.write(self.style.SUCCESS("Successfully loaded panel map"))
        self.stdout.write("Loading SV VCF file...")
        with vcfpy.Reader.from_path(self.path) as vcf_reader:
            chrom = None
            for i, record in enumerate(vcf_reader):
                if record.CHROM != chrom:
                    self.stdout.write("Starting on chrom %s" % record.CHROM)
                    chrom = record.CHROM
                if i % 100 == 0:
                    self.stdout.write("  @ {}:{:,}".format(record.CHROM, record.POS))
                self.import_sv_vcf_record(panel_map, record)
        self.stdout.write(self.style.SUCCESS("Successfully imported SV VCF file"))

    def load_panel_map(self):
        """Load and return the panel map file."""
        result = {}
        with open(self.panel_path, "rt") as inputf:
            header = None
            for line in inputf:
                if line and line[-1] == "\n":
                    line = line[:-1]
                if not line:
                    continue
                if not header:
                    header = line.strip().split("\t")
                    if header != ["sample", "pop", "super_pop", "gender"]:
                        raise CommandError("Unexpected header!")
                    continue
                else:
                    arr = line.split("\t")
                    result[arr[0]] = {"pop": arr[1], "super_pop": arr[2], "sex": arr[3]}
        return result

    def import_sv_vcf_record(self, panel_map, record):
        """Import the SV VCF file into the database."""
        # Counters
        super_pops = ("All", "AFR", "AMR", "EAS", "EUR", "SAS")
        num_samples = 0
        num_alleles = {key: 0 for key in super_pops}
        num_var_alleles = {key: 0 for key in super_pops}

        # Count statistics
        for call in record.calls:
            sample = call.sample
            gt = call.data.get("GT", ".")
            super_pop = panel_map[sample]["super_pop"]
            sex = panel_map[sample]["sex"]
            # Skip if genotype is no-call
            if gt == ".":
                continue
            # Count alleles contributed by this individual
            if record.CHROM == "X":
                this_alleles = 1 if sex == "male" else 2
            elif record.CHROM == "Y":
                this_alleles = 1 if sex == "male" else 0
            else:
                this_alleles = 2
            if this_alleles == 0:
                continue  # no alleles contributed by this individual
            # Increment allele counters
            num_alleles["All"] += this_alleles
            num_alleles[super_pop] += this_alleles
            num_samples += 1
            if gt in ("0|0", "0/0"):
                continue  # non-variant allele
            elif this_alleles == 1:
                num_var_alleles["All"] += 1
                num_alleles[super_pop] += 1
            elif "0" in gt:  # heterozygous, even if multiallelic (-> CNV)
                num_var_alleles["All"] += 1
                num_alleles[super_pop] += 1
            else:  # homozygous non-ref, even if multiallelic (-> CNV)
                num_var_alleles["All"] += 2
                num_alleles[super_pop] += 2

        # Perform the record creation
        ThousandGenomesSv.objects.create(
            release=self.genome_release,
            chromosome=record.CHROM,
            start=record.POS,
            end=record.INFO.get("END", record.POS),
            bin=binning.assign_bin(record.POS - 1, record.INFO.get("END", record.POS)),
            containing_bins=binning.containing_bins(
                record.POS - 1, record.INFO.get("END", record.POS)
            ),
            start_ci_left=record.INFO.get("CIPOS", (0, 0))[0],
            start_ci_right=record.INFO.get("CIPOS", (0, 0))[1],
            end_ci_left=record.INFO.get("CIEND", (0, 0))[0],
            end_ci_right=record.INFO.get("CIEND", (0, 0))[1],
            sv_type=record.INFO.get("SVTYPE"),
            source_call_set=record.INFO.get("CS"),
            mobile_element_info=record.INFO.get("MEINFO"),
            num_samples=num_samples,
            num_alleles=num_alleles["All"],
            num_var_alleles=num_var_alleles["All"],
            **{
                "num_alleles_%s" % key.lower(): num_alleles[key]
                for key in super_pops
                if key != "All"
            },
            **{
                "num_var_alleles_%s" % key.lower(): num_var_alleles[key]
                for key in super_pops
                if key != "All"
            },
        )


class DbVarImporter:
    """Importer for dbVar SVs."""

    def __init__(self, stdout, style, path, name, database):
        #: Output stream
        self.stdout = stdout
        #: Style...
        self.style = style
        #: Path to file to import.
        self.path = path
        #: Name of the database stored in the file.
        self.name = name
        arr = self.name.split("-")
        if (
            len(arr) != 3
            or arr[0] != "dbvar"
            or arr[1] not in ("insertions", "duplications", "deletions")
        ):
            raise CommandError("Invalid database name {}".format(name))
        #: DB configuration
        self.database = database
        #: The type of SVs to import
        self.sv_type = arr[1]
        #: The genome release to import for
        self.genome_release = arr[-1]

    def clear_db(self):
        self.stdout.write("Removing old entries...")
        if self.sv_type == "insertions":
            sv_type = "INS"
        elif self.sv_type == "deletions":
            sv_type = "DEL"
        elif self.sv_type == "duplications":
            sv_type = "DUP"
        DbVarSv.objects.filter(sv_type=sv_type, release=self.genome_release).delete()
        self.stdout.write(self.style.SUCCESS("Successfully removed old entries"))

    def perform_import(self):
        self.clear_db()
        self.stdout.write("Importing dbVar SV file...")
        with gzip.open(self.path, "rt") as inputf:
            chrom = None
            first_line = None
            second_line = None
            for i, line in enumerate(inputf):
                if line.endswith("\n"):
                    line = line[:-1]
                if not first_line:
                    first_line = line
                    if first_line != "#NR_SVs GRCh37":
                        raise CommandError("First line must be '#NR_SVs GRCh37'")
                elif not second_line:
                    second_line = line
                    if not second_line.startswith("#chr"):
                        raise CommandError("Second line must start with '#chr'")
                    header = second_line[1:].split("\t")
                else:
                    values = dict(zip(header, line.split("\t")))
                    if values["chr"] != chrom:
                        self.stdout.write("Starting on chrom %s" % values["chr"])
                        chrom = values["chr"]
                    if i % 10000 == 0:
                        self.stdout.write(
                            "  @ {}:{:,}".format(values["chr"], int(values["outermost_start"]))
                        )
                    self.create_record(values)
        self.stdout.write(self.style.SUCCESS("Successfully imported dbVar SV file"))

    def create_record(self, values):
        """Create new entry in dbVar SV table."""
        if values["clinical_assertion"]:
            clinical_assertions = values["clinical_assertion"].split(";")
        else:
            clinical_assertions = []
        if values["clinvar_accession"]:
            clinvar_accessions = values["clinvar_accession"].split(";")
        else:
            clinvar_accessions = []
        if self.sv_type == "insertions":
            extra_kwargs = {
                "min_ins_length": values["min_insertion_length"],
                "min_ins_length": values["min_insertion_length"],
            }
        else:
            extra_kwargs = {}
        DbVarSv.objects.create(
            release=self.genome_release,
            chromosome=values["chr"],
            start=values["outermost_start"],
            end=values["outermost_stop"],
            bin=binning.assign_bin(
                int(values["outermost_start"]) - 1, int(values["outermost_stop"])
            ),
            containing_bins=binning.containing_bins(
                int(values["outermost_start"]) - 1, int(values["outermost_stop"])
            ),
            num_carriers=values["variant_count"],
            sv_type=values["variant_type"],
            method=values["method"],
            analysis=values["analysis"],
            platform=values["platform"],
            study=values["study"],
            clinical_assertions=clinical_assertions,
            clinvar_accessions=clinvar_accessions,
            bin_size=values["bin_size"],
            **extra_kwargs,
        )


class GnomadSvImporter:
    """Importer for gnomAD SVs"""

    def __init__(self, stdout, style, path, name, database):
        #: Output stream
        self.stdout = stdout
        #: Style...
        self.style = style
        #: Path to file to import.
        self.path = path
        #: Name of the database stored in the file.
        self.name = name
        arr = self.name.split("-")
        if len(arr) != 2 or arr[0] != "gnomad_sv":
            raise CommandError("Invalid database name {}".format(name))
        #: DB configuration
        self.database = database
        #: The genome release to import for
        self.genome_release = arr[-1]

    def clear_db(self):
        self.stdout.write("Removing old entries...")
        GnomAdSv.objects.filter(release=self.genome_release).delete()
        self.stdout.write(self.style.SUCCESS("Successfully removed old entries"))

    def perform_import(self):
        self.clear_db()
        self.stdout.write("Importing gnomAD SV file...")
        prev_chrom = None
        with vcfpy.Reader.from_path(self.path) as reader:
            for i, record in enumerate(reader):
                self._create_record(record)
                if prev_chrom != record.CHROM:
                    self.stdout.write("Now on chrom chr%s" % record.CHROM)
                if i % 1000 == 0:
                    print("  now @ chr{}:{:,}".format(record.CHROM, record.POS))
                prev_chrom = record.CHROM
        self.stdout.write(self.style.SUCCESS("Successfully imported gnomAD SV file"))

    def _create_record(self, record):
        """Create new entry in gnomAD SV table."""
        GnomAdSv.objects.create(
            release=self.genome_release,
            chromosome=record.CHROM,
            start=record.POS,
            end=record.INFO.get("END"),
            bin=binning.assign_bin(record.INFO.get("END") - 1, record.POS),
            containing_bins=binning.containing_bins(record.INFO.get("END") - 1, record.POS),
            ref=record.REF,
            alt=[str(x) for x in record.ALT],
            name=record.ID,
            svtype=record.INFO.get("SVTYPE"),
            svlen=record.INFO.get("SVLEN"),
            filter=record.FILTER,
            evidence=record.INFO.get("EVIDENCE"),
            algorithms=record.INFO.get("ALGORITHMS"),
            chr2=record.INFO.get("CHR2"),
            cpx_type=record.INFO.get("CPX_TYPE"),
            cpx_intervals=record.INFO.get("CPX_INTERVALS"),
            source=record.INFO.get("SOURCE"),
            strands=record.INFO.get("STRANDS"),
            unresolved_type=record.INFO.get("UNRESOLVED_TYPE"),
            pcrplus_depleted=record.INFO.get("PCRPLUS_DEPLETED", False),
            pesr_gt_overdispersion=record.INFO.get("PESR_GT_OVERDISPERSION", False),
            protein_coding_lof=record.INFO.get("PROTEIN_CODING_LOF", []),
            protein_coding_dup_lof=record.INFO.get("PROTEIN_CODING__DUP_LOF", []),
            protein_coding_copy_gain=record.INFO.get("PROTEIN_CODING__COPY_GAIN", []),
            protein_coding_dup_partial=record.INFO.get("PROTEIN_CODING__DUP_PARTIAL", []),
            protein_coding_msv_exon_ovr=record.INFO.get("PROTEIN_CODING__MSV_EXON_OVR", []),
            protein_coding_intronic=record.INFO.get("PROTEIN_CODING__INTRONIC", []),
            protein_coding_inv_span=record.INFO.get("PROTEIN_CODING__INV_SPAN", []),
            protein_coding_utr=record.INFO.get("PROTEIN_CODING__UTR", []),
            protein_coding_nearest_tss=record.INFO.get("PROTEIN_CODING__NEAREST_TSS", []),
            protein_coding_intergenic=record.INFO.get("PROTEIN_CODING__INTERGENIC", False),
            protein_coding_promoter=record.INFO.get("PROTEIN_CODING__PROMOTER", []),
            an=record.INFO.get("AN"),
            ac=record.INFO.get("AC"),
            af=record.INFO.get("AF"),
            n_bi_genos=record.INFO.get("N_BI_GENOS", 0),
            n_homref=record.INFO.get("N_HOMREF", 0),
            n_het=record.INFO.get("N_HET", 0),
            n_homalt=record.INFO.get("N_HOMALT", 0),
            freq_homref=record.INFO.get("FREQ_HOMREF", 0.0),
            freq_het=record.INFO.get("FREQ_HET", 0.0),
            freq_homalt=record.INFO.get("FREQ_HOMALT", 0.0),
            popmax_af=record.INFO.get("POPMAX_AF", 0.0),
            afr_an=record.INFO.get("AFR_AN"),
            afr_ac=record.INFO.get("AFR_AC"),
            afr_af=record.INFO.get("AFR_AF"),
            afr_n_bi_genos=record.INFO.get("AFR_N_BI_GENOS", 0),
            afr_n_homref=record.INFO.get("AFR_N_HOMREF", 0),
            afr_n_het=record.INFO.get("AFR_N_HET", 0),
            afr_n_homalt=record.INFO.get("AFR_N_HOMALT", 0),
            afr_freq_homref=record.INFO.get("AFR_FREQ_HOMREF", 0.0),
            afr_freq_het=record.INFO.get("AFR_FREQ_HET", 0.0),
            afr_freq_homalt=record.INFO.get("AFR_FREQ_HOMALT", 0.0),
            amr_an=record.INFO.get("AMR_AN"),
            amr_ac=record.INFO.get("AMR_AC"),
            amr_af=record.INFO.get("AMR_AF"),
            amr_n_bi_genos=record.INFO.get("AMR_N_BI_GENOS", 0),
            amr_n_homref=record.INFO.get("AMR_N_HOMREF", 0),
            amr_n_het=record.INFO.get("AMR_N_HET", 0),
            amr_n_homalt=record.INFO.get("AMR_N_HOMALT", 0),
            amr_freq_homref=record.INFO.get("AMR_FREQ_HOMREF", 0.0),
            amr_freq_het=record.INFO.get("AMR_FREQ_HET", 0.0),
            amr_freq_homalt=record.INFO.get("AMR_FREQ_HOMALT", 0.0),
            eas_an=record.INFO.get("EAS_AN"),
            eas_ac=record.INFO.get("EAS_AC"),
            eas_af=record.INFO.get("EAS_AF"),
            eas_n_bi_genos=record.INFO.get("EAS_N_BI_GENOS", 0),
            eas_n_homref=record.INFO.get("EAS_N_HOMREF", 0),
            eas_n_het=record.INFO.get("EAS_N_HET", 0),
            eas_n_homalt=record.INFO.get("EAS_N_HOMALT", 0),
            eas_freq_homref=record.INFO.get("EAS_FREQ_HOMREF", 0.0),
            eas_freq_het=record.INFO.get("EAS_FREQ_HET", 0.0),
            eas_freq_homalt=record.INFO.get("EAS_FREQ_HOMALT", 0.0),
            eur_an=record.INFO.get("EUR_AN"),
            eur_ac=record.INFO.get("EUR_AC"),
            eur_af=record.INFO.get("EUR_AF"),
            eur_n_bi_genos=record.INFO.get("EUR_N_BI_GENOS", 0),
            eur_n_homref=record.INFO.get("EUR_N_HOMREF", 0),
            eur_n_het=record.INFO.get("EUR_N_HET", 0),
            eur_n_homalt=record.INFO.get("EUR_N_HOMALT", 0),
            eur_freq_homref=record.INFO.get("EUR_FREQ_HOMREF", 0.0),
            eur_freq_het=record.INFO.get("EUR_FREQ_HET", 0.0),
            eur_freq_homalt=record.INFO.get("EUR_FREQ_HOMALT", 0.0),
            oth_an=record.INFO.get("OTH_AN"),
            oth_ac=record.INFO.get("OTH_AC"),
            oth_af=record.INFO.get("OTH_AF"),
            oth_n_bi_genos=record.INFO.get("OTH_N_BI_GENOS", 0),
            oth_n_homref=record.INFO.get("OTH_N_HOMREF", 0),
            oth_n_het=record.INFO.get("OTH_N_HET", 0),
            oth_n_homalt=record.INFO.get("OTH_N_HOMALT", 0),
            oth_freq_homref=record.INFO.get("OTH_FREQ_HOMREF", 0.0),
            oth_freq_het=record.INFO.get("OTH_FREQ_HET", 0.0),
            oth_freq_homalt=record.INFO.get("OTH_FREQ_HOMALT", 0.0),
        )


class Command(BaseCommand):
    """Django management command for the import of structural variant databases."""

    help = "Import of structural variant databases"

    #: The supported database releases by file name.
    databases = {
        "DGV.GS.March2016.50percent.GainLossSep.Final.hg19.gff3": {
            "genomebuild": "GRCh37",
            "name": "dgv-gs-GRCh37",
            "table": "DgvGoldStandardSvs",
            "release": "20160515",
            "importer": DgvGoldStandardImporter,
        },
        "GRCh37_hg19_variants_2016-05-15.txt": {
            "genomebuild": "GRCh37",
            "name": "dgv-GRCh37",
            "table": "DgvSvs",
            "release": "20160515",
            "importer": DgvImporter,
        },
        "GRCh38_hg38_variants_2016-08-31.txt": {
            "genomebuild": "GRCh38",
            "name": "dgv-GRCh38",
            "table": "DgvSvs",
            "release": "20160831",
            "importer": DgvImporter,
        },
        "exac-final.autosome-1pct-sq60-qc-prot-coding.cnv.bed": {
            "genomebuild": "GRCh37",
            "name": "exac-GRCh37",
            "table": "ExacCnv",
            "release": "release1",
            "importer": ExacCnvImporter,
        },
        "ALL.wgs.mergedSV.v8.20130502.svs.genotypes.vcf.gz": {
            "genomebuild": "GRCh37",
            "name": "thousand-genomes-svs-GRCh37",
            "table": "ThousandGenomesSv",
            "release": "v8.20130502",
            "importer": ThousandGenomesImporter,
        },
        "GRCh37.nr_deletions.tsv.gz": {
            "genomebuild": "GRCh37",
            "name": "dbvar-deletions-GRCh37",
            "table": "DbVarSv",
            "release": "v0.20180824",
            "importer": DbVarImporter,
        },
        "GRCh37.nr_duplications.tsv.gz": {
            "genomebuild": "GRCh37",
            "name": "dbvar-duplications-GRCh37",
            "table": "DbVarSv:duplication",
            "release": "v0.20180824",
            "importer": DbVarImporter,
        },
        "GRCh37.nr_insertions.tsv.gz": {
            "genomebuild": "GRCh37",
            "name": "dbvar-insertions-GRCh37",
            "table": "DbVarSv:insertions",
            "release": "v0.20180824",
            "importer": DbVarImporter,
        },
        "GRCh38.nr_deletions.tsv.gz": {
            "genomebuild": "GRCh38",
            "name": "dbvar-deletions-GRCh38",
            "table": "DbVarSv:deletions",
            "release": "v0.20180824",
            "importer": DbVarImporter,
        },
        "GRCh38.nr_duplications.tsv.gz": {
            "genomebuild": "GRCh38",
            "name": "dbvar-duplications-GRCh38",
            "table": "DbVarSv:duplications",
            "release": "v0.update20180824",
            "importer": DbVarImporter,
        },
        "GRCh38.nr_insertions.tsv.gz": {
            "genomebuild": "GRCh38",
            "name": "dbvar-insertions-GRCh38",
            "table": "DbVarSv:insertions",
            "release": "v0.20180824",
            "importer": DbVarImporter,
        },
        "gnomad_v2_sv.sites.vcf.gz": {
            "genomebuild": "GRCh37",
            "name": "gnomad_sv-GRCh37",
            "table": "GnomAdSv",
            "release": "v2",
            "importer": GnomadSvImporter,
        },
    }

    def add_arguments(self, parser):
        path_help = (
            "Structural variants are directly imported from their source file version. The database release will be "
            "detected from the file names. The following file names are currently known: "
            + ", ".join(self.databases.keys())
        )

        parser.add_argument("--path", help="Input file path " + path_help, required=True)
        parser.add_argument("--thousand-genomes-panel", help="Path to thousand genomes panel file")
        parser.add_argument("--comment", help="Comment for the imported database")
        parser.add_argument(
            "--force", help="Force import, discarding old data", action="store_true", default=False
        )

    @transaction.atomic
    def handle(self, *args, **options):
        database = self.databases.get(os.path.basename(options["path"]))
        if not database:
            raise CommandError(
                "File name {} is not known".format(os.path.basename(options["path"]))
            )

        # Optional arguments for certain importers
        kwargs = {}
        if database["name"] == "thousand-genomes-svs-GRCh37":
            if "thousand_genomes_panel" not in options:
                raise CommandError(
                    "For thousand genomes, you have to give --thousand-genomes-panel"
                )
            kwargs["panel_path"] = options["thousand_genomes_panel"]
        importer = database["importer"](
            stdout=self.stdout,
            style=self.style,
            path=options["path"],
            name=database["name"],
            database=database,
            **kwargs,
        )

        # Check for conflicts with previous import.
        values = {
            "genomebuild": database["genomebuild"],
            "table": database["table"],
            "timestamp": timezone.now(),
            "release": database["release"],
            "comment": options["comment"] if options["comment"] else "",
        }
        infos = ImportInfo.objects.filter(
            genomebuild=values["genomebuild"], table=values["table"], release=values["release"]
        )
        if infos and not options["force"]:
            raise CommandError("This import already exists!")

        # Perform the actual import.
        importer.perform_import()

        # Update import info or create new one.
        if infos:
            infos.delete()
        ImportInfo.objects.create(**values)
