"""Factory Boy factory classes for ``svdbs``."""

import binning
import factory

from ..models import (
    DgvGoldStandardSvs,
    DgvSvs,
    ExacCnv,
    ThousandGenomesSv,
    DbVarSv,
    GnomAdSv,
    EXAC_POP_CHOICES,
)


class DgvGoldStandardSvsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DgvGoldStandardSvs

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start_outer = factory.Sequence(lambda n: (n + 1) * 100 - 10)
    start_inner = factory.Sequence(lambda n: (n + 1) * 100 + 10)
    end_inner = factory.Sequence(lambda n: (n + 1) * 100 + 90)
    end_outer = factory.Sequence(lambda n: (n + 1) * 100 + 110)

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100 - 11, (n + 1) * 100 + 110))
    containing_bins = factory.Sequence(
        lambda n: binning.containing_bins((n + 1) * 100 - 11, (n + 1) * 100 + 110)
    )

    accession = factory.Sequence(lambda n: "DGV-GS-%d" % n)
    sv_type = "DEL"
    sv_sub_type = "DEL"
    num_studies = 1
    studies = factory.Sequence(lambda n: ["DGV-GS-STUDY-%d" % n])
    num_platforms = 1
    platforms = factory.Sequence(lambda n: ["DGV-GS-PLATFORM-%d" % n])
    num_algorithms = 1
    algorithms = factory.Sequence(lambda n: ["DGV-GS-ALGO-%d" % n])
    num_variants = 1
    num_carriers = 1
    num_unique_samples = 1
    num_carriers_african = 0
    num_carriers_asian = 0
    num_carriers_european = 0
    num_carriers_mexican = 0
    num_carriers_middle_east = 1
    num_carriers_native_american = 0
    num_carriers_north_american = 0
    num_carriers_oceania = 0
    num_carriers_south_american = 0
    num_carriers_admixed = 0
    num_carriers_unknown = 0


class DgvSvsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DgvSvs

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100, (n + 1) * 100 + 100))
    containing_bins = factory.Sequence(
        lambda n: binning.containing_bins((n + 1) * 100, (n + 1) * 100 + 100)
    )

    accession = factory.Sequence(lambda n: "DGV-%d" % n)
    sv_type = "DEL"
    sv_sub_type = "DEL"

    study = factory.Sequence(lambda n: "DGV-STUDY-%d" % n)
    platform = factory.Sequence(lambda n: ["DGV-PLATFORM-%d" % n])

    num_samples = 1
    observed_gains = 0
    observed_losses = 1


class ExacCnvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExacCnv

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100, (n + 1) * 100 + 100))
    containing_bins = factory.Sequence(
        lambda n: binning.containing_bins((n + 1) * 100, (n + 1) * 100 + 100)
    )

    sv_type = "DEL"
    population = factory.Iterator([x[0] for x in EXAC_POP_CHOICES])
    phred_score = factory.Iterator(list(range(30)))


class ThousandGenomesSvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ThousandGenomesSv

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100, (n + 1) * 100 + 100))
    containing_bins = factory.Sequence(
        lambda n: binning.containing_bins((n + 1) * 100, (n + 1) * 100 + 100)
    )

    start_ci_left = -100
    start_ci_right = 100
    end_ci_left = -100
    end_ci_right = 100

    sv_type = "DEL"
    source_call_set = "DEL_delly"

    mobile_element_info = []

    num_samples = 1
    num_alleles = 2
    num_var_alleles = 1

    num_alleles_afr = 2
    num_var_alleles_afr = 1
    num_alleles_amr = 0
    num_var_alleles_amr = 0
    num_alleles_eas = 0
    num_var_alleles_eas = 0
    num_alleles_eur = 0
    num_var_alleles_eur = 0
    num_alleles_sas = 0
    num_var_alleles_sas = 0


class DbVarSvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DbVarSv

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100, (n + 1) * 100 + 100))
    containing_bins = factory.Sequence(
        lambda n: binning.containing_bins((n + 1) * 100, (n + 1) * 100 + 100)
    )

    num_carriers = 1
    sv_type = "DEL"
    method = "Sequencing"
    analysis = "Read_depth"
    platform = factory.Sequence(lambda n: "DBVAR-PLATFORM-%d" % n)
    study = factory.Sequence(lambda n: "DBVAR-STUDY-%d" % n)
    clinical_assertions = []
    clinvar_accessions = []
    bin_size = "large"
    min_ins_length = None
    max_ins_length = None


class GnomAdSvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GnomAdSv

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100, (n + 1) * 100 + 100))
    containing_bins = factory.Sequence(
        lambda n: binning.containing_bins((n + 1) * 100, (n + 1) * 100 + 100)
    )

    ref = "N"
    alt = ["<DUP>"]

    name = factory.Sequence(lambda n: "DBVAR-SV-%d" % n)
    svtype = "DEL"
    svlen = 100
    filter = ["PASS"]
    evidence = ["BAF", "RD"]
    algorithms = ["depth"]
    chr2 = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    cpx_type = None
    cpx_intervals = []
    source = None
    strands = None
    unresolved_type = None
    pcrplus_depleted = False
    pesr_gt_overdispersion = False
    protein_coding_lof = []
    protein_coding_dup_lof = []
    protein_coding_copy_gain = []
    protein_coding_dup_partial = []
    protein_coding_msv_exon_ovr = []
    protein_coding_intronic = []
    protein_coding_inv_span = []
    protein_coding_utr = []
    protein_coding_nearest_tss = []
    protein_coding_intergenic = False
    protein_coding_promoter = []
    an = 2
    ac = [1]
    af = [0.5]
    n_bi_genos = 1
    n_homref = 0
    n_het = 1
    n_homalt = 0
    freq_homref = 0.5
    freq_het = 0.5
    freq_homalt = 0.0
    popmax_af = 0.5
    afr_an = 1
    afr_ac = [1]
    afr_af = [0.5]
    afr_n_bi_genos = 0
    afr_n_homref = 0
    afr_n_het = 0
    afr_n_homalt = 0
    afr_freq_homref = 0.0
    afr_freq_het = 0.0
    afr_freq_homalt = 0.0
    amr_an = 0
    amr_ac = [0]
    amr_af = [0.0]
    amr_n_bi_genos = 0
    amr_n_homref = 0
    amr_n_het = 0
    amr_n_homalt = 0
    amr_freq_homref = 0.0
    amr_freq_het = 0.0
    amr_freq_homalt = 0.0
    eas_an = 0
    eas_ac = [0]
    eas_af = [0.0]
    eas_n_bi_genos = 0
    eas_n_homref = 0
    eas_n_het = 0
    eas_n_homalt = 0
    eas_freq_homref = 0.0
    eas_freq_het = 0.0
    eas_freq_homalt = 0.0
    eur_an = 0
    eur_ac = [0]
    eur_af = [0.0]
    eur_n_bi_genos = 0
    eur_n_homref = 0
    eur_n_het = 0
    eur_n_homalt = 0
    eur_freq_homref = 0.0
    eur_freq_het = 0.0
    eur_freq_homalt = 0.0
    oth_an = 0
    oth_ac = [0]
    oth_af = [0.0]
    oth_n_bi_genos = 0
    oth_n_homref = 0
    oth_n_het = 0
    oth_n_homalt = 0
    oth_freq_homref = 0.0
    oth_freq_het = 0.0
    oth_freq_homalt = 0.0
