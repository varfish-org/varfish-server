"""Django command for checking installation."""

from enum import Enum

from django.core.management.base import BaseCommand
from django.db import ProgrammingError, connection, transaction

ICON_CHECK_MARK = "\u2714"
ICON_FAILED = "\u2718"


class State(Enum):
    SUCCESS = "success"
    FAIL = "fail"


INDEXES_SMALLVARIANT = (
    "variants_sm_case_id_071d6b_gin",
    "variants_sm_case_id_1f4f31_idx",
    "variants_sm_case_id_3efbb1_idx",
    "variants_sm_case_id_423a80_idx",
    "variants_sm_case_id_5d52f6_idx",
    "variants_sm_case_id_6f9d8c_idx",
    "variants_sm_case_id_a529e8_gin",
    "variants_sm_chromosome_no_idx",
    "variants_sm_coordinates",
)

INDEXES_STRUCTURALVARIANT = (
    "svs_structu_case_id_988c93_idx",
    "svs_structu_case_id_aa8632_idx",
    "svs_structu_case_id_cd8553_idx",
    "svs_structu_set_id_951ec1_idx",
    "svs_structuralvariant_sv_uuid_key",
)

INDEXES_CASE = (
    "variants_case_pkey",
    "variants_case_sodar_uuid_key",
    "variants_ca_name_89b7c1_idx",
    "variants_case_project_id_64ceb9ce",
    "variants_case_search_tokens_7cbf90f1",
    "variants_case_latest_structural_variant_set_id_c92f9810",
    "variants_case_latest_variant_set_id_65a85e18",
)

INDEXES_GENEIDINHPO = (
    "geneinfo_geneidinhpo_ensembl_gene_id",
    "geneinfo_geneidinhpo_entrez_id",
)

INDEXES_GENEIDTOINHERITANCE = (
    "geneinfo_geneidtoinheritance_mode_of_inheritance",
    "geneinfo_geneidtoinheritance_entrez_id",
    "geneinfo_geneidtoinheritance_ensembl_gene_id",
)

INDEXES_MGIMAPPING = ("geneinfo_mgimapping_human_entrez_id_idx",)

INDEXES_SMALLVARIANTSUMMARY = ("variants_smallvariantsummary_coord",)

INDEXES_SVS_THOUSAND_GENOMES = ("svdbs_thous_release_fadfda_idx",)

INDEXES_SVS_GNOMAD = ("svdbs_gnoma_release_b9bf46_idx",)

INDEXES_EXACCNV = ("svdbs_exacc_release_c8af19_idx",)

INDEXES_DGVSVS = ("svdbs_dgvsv_release_2fc196_idx",)

INDEXES_DGVGOLDSTANDARD = ("svdbs_dgvgo_release_a7129f_idx",)

INDEXES_DBVAR = ("svdbs_dbvar_release_72ea5e_idx",)

INDEXES_HPONAME = ("geneinfo_hp_name_922635_idx", "geneinfo_hp_hpo_id_5b82f3_idx")

INDEXES_NCBIGENERIF = ("geneinfo_nc_entrez__79134c_idx",)

INDEXES_NCBIGENEINFO = ("geneinfo_nc_entrez__e13b8a_idx",)

INDEXES_REFSEQTOGENESYMBOL = ("geneinfo_re_entrez__3b440a_idx",)

INDEXES_ENSEMBLTOGENESYMBOL = ("geneinfo_en_ensembl_9b7f1b_idx",)

INDEXES_HGNC = (
    "geneinfo_hg_entrez__91b58b_idx",
    "geneinfo_hg_ucsc_id_7a67bb_idx",
    "geneinfo_hg_hgnc_id_e02c9b_idx",
    "geneinfo_hg_ensembl_d4d39c_idx",
    "geneinfo_hg_symbol_0a5edc_idx",
    "geneinfo_hg_ensembl_d28f87_idx",
)

INDEXES_ACMG = ("geneinfo_ac_entrez__fa95a2_idx", "geneinfo_ac_ensembl_f71c79_idx")

INDEXES_REFSEQTOHGNC = ("geneinfo_re_entrez__98dd58_idx", "geneinfo_re_hgnc_id_5906c2_idx")

INDEXES_HPO = ("geneinfo_hp_omim_id_b96394_idx", "geneinfo_hp_databas_ab9ccc_idx")

INDEXES_MIM2GENEMEDGEN = ("geneinfo_mi_entrez__df3c2a_idx",)

INDEXES_EXACCONSTRAINTS = ("geneinfo_ex_ensembl_40f907_idx",)

INDEXES_GNOMADCONSTRAINTS = ("geneinfo_gn_ensembl_561533_idx",)

INDEXES_EXAC = ()

INDEXES_GNOMADEXOMES = ()

INDEXES_GNOMADGENOMES = ()

INDEXES_THOUSANDGENOMES = ()

INDEXES_VISTAENHANCER = ("genomicfeat_release_e3899e_idx",)

INDEXES_GENEINTERVAL = (
    "genomicfeat_databas_9e9301_idx",
    "genomicfeat_gene_id_87aab6_idx",
)

INDEXES_ENSEMBLREGULATORYFEATURE = ("genomicfeat_release_87d7b8_idx",)

INDEXES_TADINTERVAL = ("genomicfeat_release_bef485_idx",)

INDEXES_TADBOUNDARYINTERVAL = ("genomicfeat_release_472cf6_idx",)

INDEXES_KNOWNGENEAA = (
    "conservatio_release_ce232d_idx",
    "conservatio_transcr_8aa7d7_idx",
)

INDEXES_STRUCTURALVARIANTGENEANNOTATION = (
    "svs_structu_sv_uuid_09c0c4_idx",
    "svs_structu_set_id_42f2ba_idx",
)

INDEXES_STRUCTURALVARIANTFLAGS = ("svs_structu_case_id_94fcb3_idx",)

INDEXES_STRUCTURALVARIANTCOMMENT = ("svs_structu_case_id_7fdf69_idx",)

INDEXES_CASEALIGNMENTSTATS = ("variants_ca_case_id_42432f_idx",)

INDEXES_CLINVAR = (
    "clinvar_cli_release_1f6a94_idx",
    "clinvar_cli_release_1f6a94_idx",
)

INDEXES_REFSEQTOKEGG = ("pathways_re_gene_id_86cbb2_idx",)

INDEXES_ENSEMBLTOKEGG = ("pathways_en_gene_id_20f7c2_idx",)

INDEXES_DBSNP = "dbsnp_dbsnp_release_chromosome_start_51af7d8b_uniq"

EXPECTED_INDEXES = {
    "variants_smallvariant": INDEXES_SMALLVARIANT,
    "svs_structuralvariant": INDEXES_STRUCTURALVARIANT,
    "variants_case": INDEXES_CASE,
    "geneinfo_geneidinhpo": INDEXES_GENEIDINHPO,
    "geneinfo_geneidtoinheritance": INDEXES_GENEIDTOINHERITANCE,
    "geneinfo_mgimapping": INDEXES_MGIMAPPING,
    "variants_smallvariantsummary": INDEXES_SMALLVARIANTSUMMARY,
    "svdbs_thousandgenomessv": INDEXES_SVS_THOUSAND_GENOMES,
    "svdbs_gnomadsv": INDEXES_SVS_GNOMAD,
    "svdbs_exaccnv": INDEXES_EXACCNV,
    "svdbs_dgvsv": INDEXES_DGVSVS,
    "svdbs_dgvgoldstandardsvs": INDEXES_DGVGOLDSTANDARD,
    "svdbs_dbvarsv": INDEXES_DBVAR,
    "geneinfo_hponame": INDEXES_HPONAME,
    "geneinfo_ncbigenerif": INDEXES_NCBIGENERIF,
    "geneinfo_ncbigeneinfo": INDEXES_NCBIGENEINFO,
    "geneinfo_refseqtogenesymbol": INDEXES_REFSEQTOGENESYMBOL,
    "geneinfo_ensembltogenesymbol": INDEXES_ENSEMBLTOGENESYMBOL,
    "geneinfo_hgnc": INDEXES_HGNC,
    "geneinfo_acmg": INDEXES_ACMG,
    "geneinfo_refseqtohgnc": INDEXES_REFSEQTOHGNC,
    "geneinfo_hpo": INDEXES_HPO,
    "geneinfo_mim2genemedgen": INDEXES_MIM2GENEMEDGEN,
    "geneinfo_exacconstraints": INDEXES_EXACCONSTRAINTS,
    "geneinfo_gnomadconstraints": INDEXES_GNOMADCONSTRAINTS,
    "frequencies_exac": INDEXES_EXAC,
    "frequencies_gnomadexomes": INDEXES_GNOMADEXOMES,
    "frequencies_gnomadgenomes": INDEXES_GNOMADGENOMES,
    "frequencies_thousandgenomes": INDEXES_THOUSANDGENOMES,
    "genomicfeatures_vistaenhancer": INDEXES_VISTAENHANCER,
    "genomicfeatures_ensemblregulatoryfeature": INDEXES_ENSEMBLREGULATORYFEATURE,
    "genomicfeatures_tadinterval": INDEXES_TADINTERVAL,
    "genomicfeatures_tadboundaryinterval": INDEXES_TADBOUNDARYINTERVAL,
    "genomicfeatures_geneinterval": INDEXES_GENEINTERVAL,
    "conservation_knowngeneaa": INDEXES_KNOWNGENEAA,
    "svs_structuralvariantgeneannotation": INDEXES_STRUCTURALVARIANTGENEANNOTATION,
    "svs_structuralvariantflags": INDEXES_STRUCTURALVARIANTFLAGS,
    "svs_structuralvariantcomment": INDEXES_STRUCTURALVARIANTCOMMENT,
    "variants_casealignmentstats": INDEXES_CASEALIGNMENTSTATS,
    "clinvar_clinvar": INDEXES_CLINVAR,
    "pathways_refseqtokegg": INDEXES_REFSEQTOKEGG,
    "pathways_ensembltokegg": INDEXES_ENSEMBLTOKEGG,
    "dbsnp_dbsnp": INDEXES_DBSNP,
}


class Command(BaseCommand):
    """Implementation of checking installation."""

    #: Help message displayed on the command line.
    help = "Sanity check installation."

    def state_format(self, state, msg):
        if state == state.SUCCESS:
            return self.style.SUCCESS("%s %s" % (ICON_CHECK_MARK, msg))
        elif state == state.FAIL:
            return self.style.ERROR("%s %s" % (ICON_FAILED, msg))
        return msg

    def check_datatype(self, cursor, table, field, expected):
        try:
            query = (
                "SELECT data_type FROM information_schema.columns WHERE table_name = '%s' AND column_name = '%s'"
                % (table, field)
            )
            cursor.execute(query)
            x = cursor.fetchone()
            if x:
                state = State.SUCCESS if x[0] == expected else State.FAIL
                self.stdout.write(self.state_format(state, "%s.%s is %s" % (table, field, x[0])))
            else:
                self.stdout.write(
                    self.state_format(State.FAIL, "query '%s' returned empty results")
                )
        except ProgrammingError as e:
            self.stdout.write(self.state_format(State.FAIL, "query '%s' failed: %s" % e))

    def check_index(self, cursor, table, index):
        try:
            query = (
                "SELECT COUNT(*) FROM pg_indexes WHERE tablename = '%s' and indexname = '%s'"
                % (table, index)
            )
            cursor.execute(query)
            x = cursor.fetchone()
            if x:
                self.stdout.write(
                    self.state_format(
                        State.SUCCESS if x[0] == 1 else State.FAIL, "%s: %s" % (table, index)
                    )
                )
            else:
                self.stdout.write(
                    self.state_format(State.FAIL, "query '%s' returned empty results")
                )
        except ProgrammingError as e:
            self.stdout.write(self.state_format(State.FAIL, "query '%s' failed: %s" % e))

    @transaction.atomic
    def handle(self, *args, **options):
        """Perform rebuilding the statistics."""
        with connection.cursor() as cursor:
            self.stdout.write("Checking data types ...")
            self.check_datatype(cursor, "variants_smallvariant", "id", "bigint")
            self.check_datatype(cursor, "svs_structuralvariant", "id", "bigint")
            self.stdout.write("Checking indexes ...")
            for table, indexes in EXPECTED_INDEXES.items():
                for index in indexes:
                    self.check_index(cursor, table, index)
