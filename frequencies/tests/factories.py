"""Factory Boy factory classes for ``frequencies``."""

import factory

from variants.tests.factories_data import SMALL_VARS, small_var_iterator, small_var_attribute

from ..models import Exac, GnomadExomes, GnomadGenomes, ThousandGenomes

#: The gene to create the frequencies for.
SYMBOL = "LAMA1"

#: Number of variants to generate frequencies for.
NUM_VARIANTS = len(SMALL_VARS[SYMBOL]["position"])

#: Base data for ExAC and gnomAD data.
MACARTHUR_VARS = {
    SYMBOL: {
        "ac": [1] * NUM_VARIANTS,
        "ac_amr": [0] * NUM_VARIANTS,
        "ac_eas": [0] * NUM_VARIANTS,
        "ac_fin": [0] * NUM_VARIANTS,
        "ac_nfe": [0] * NUM_VARIANTS,
        "ac_oth": [0] * NUM_VARIANTS,
        "an": [None] * NUM_VARIANTS,
        "an_afr": [8726] * NUM_VARIANTS,
        "an_amr": [838] * NUM_VARIANTS,
        "an_eas": [1620] * NUM_VARIANTS,
        "an_fin": [3464] * NUM_VARIANTS,
        "an_nfe": [14996] * NUM_VARIANTS,
        "an_oth": [982] * NUM_VARIANTS,
        "hemi": [None] * NUM_VARIANTS,
        "hemi_afr": [None] * NUM_VARIANTS,
        "hemi_amr": [None] * NUM_VARIANTS,
        "hemi_eas": [None] * NUM_VARIANTS,
        "hemi_fin": [None] * NUM_VARIANTS,
        "hemi_nfe": [None] * NUM_VARIANTS,
        "hemi_oth": [None] * NUM_VARIANTS,
        "hom": [0] * NUM_VARIANTS,
        "hom_afr": [0] * NUM_VARIANTS,
        "hom_amr": [0] * NUM_VARIANTS,
        "hom_eas": [0] * NUM_VARIANTS,
        "hom_fin": [0] * NUM_VARIANTS,
        "hom_nfe": [0] * NUM_VARIANTS,
        "hom_oth": [0] * NUM_VARIANTS,
        "popmax": ["AFR"] * NUM_VARIANTS,
        "ac_popmax": [1] * NUM_VARIANTS,
        "an_popmax": [8726] * NUM_VARIANTS,
        "af_popmax": [0.0001146] * NUM_VARIANTS,
        "hemi_popmax": [None] * NUM_VARIANTS,
        "hom_popmax": [0] * NUM_VARIANTS,
        "af": [None] * NUM_VARIANTS,
        "af_afr": [0.0001146] * NUM_VARIANTS,
        "af_amr": [0.0] * NUM_VARIANTS,
        "af_eas": [0.0] * NUM_VARIANTS,
        "af_fin": [0.0] * NUM_VARIANTS,
        "af_nfe": [0.0] * NUM_VARIANTS,
        "af_oth": [0.0] * NUM_VARIANTS,
    }
}


def ma_var_iterator(gene, attribute):
    """Return ``factory.Iterator`` for the given gene and attribute."""
    return factory.Iterator(MACARTHUR_VARS[gene][attribute])


class MacArthurFrequenciesFactoryBase(factory.django.DjangoModelFactory):
    """Base class for the ``frequencies``'s from ExAC and gnomAD."""

    class Meta:
        abstract = True

    release = small_var_attribute(SYMBOL, "release")
    chromosome = small_var_attribute(SYMBOL, "chromosome")
    position = small_var_iterator(SYMBOL, "position")
    reference = small_var_iterator(SYMBOL, "reference")
    alternative = small_var_iterator(SYMBOL, "alternative")

    ac = ma_var_iterator(SYMBOL, "ac")
    ac_amr = ma_var_iterator(SYMBOL, "ac_amr")
    ac_eas = ma_var_iterator(SYMBOL, "ac_eas")
    ac_fin = ma_var_iterator(SYMBOL, "ac_fin")
    ac_nfe = ma_var_iterator(SYMBOL, "ac_nfe")
    ac_oth = ma_var_iterator(SYMBOL, "ac_oth")
    an = ma_var_iterator(SYMBOL, "an")
    an_afr = ma_var_iterator(SYMBOL, "an_afr")
    an_amr = ma_var_iterator(SYMBOL, "an_amr")
    an_eas = ma_var_iterator(SYMBOL, "an_eas")
    an_fin = ma_var_iterator(SYMBOL, "an_fin")
    an_nfe = ma_var_iterator(SYMBOL, "an_nfe")
    an_oth = ma_var_iterator(SYMBOL, "an_oth")
    hemi = ma_var_iterator(SYMBOL, "hemi")
    hemi_afr = ma_var_iterator(SYMBOL, "hemi_afr")
    hemi_amr = ma_var_iterator(SYMBOL, "hemi_amr")
    hemi_eas = ma_var_iterator(SYMBOL, "hemi_eas")
    hemi_fin = ma_var_iterator(SYMBOL, "hemi_fin")
    hemi_nfe = ma_var_iterator(SYMBOL, "hemi_nfe")
    hemi_oth = ma_var_iterator(SYMBOL, "hemi_oth")
    hom = ma_var_iterator(SYMBOL, "hom")
    hom_afr = ma_var_iterator(SYMBOL, "hom_afr")
    hom_amr = ma_var_iterator(SYMBOL, "hom_amr")
    hom_eas = ma_var_iterator(SYMBOL, "hom_eas")
    hom_fin = ma_var_iterator(SYMBOL, "hom_fin")
    hom_nfe = ma_var_iterator(SYMBOL, "hom_nfe")
    hom_oth = ma_var_iterator(SYMBOL, "hom_oth")
    popmax = ma_var_iterator(SYMBOL, "popmax")
    ac_popmax = ma_var_iterator(SYMBOL, "ac_popmax")
    an_popmax = ma_var_iterator(SYMBOL, "an_popmax")
    af_popmax = ma_var_iterator(SYMBOL, "af_popmax")
    hemi_popmax = ma_var_iterator(SYMBOL, "hemi_popmax")
    hom_popmax = ma_var_iterator(SYMBOL, "hom_popmax")
    af = ma_var_iterator(SYMBOL, "af")
    af_afr = ma_var_iterator(SYMBOL, "af_afr")
    af_amr = ma_var_iterator(SYMBOL, "af_amr")
    af_eas = ma_var_iterator(SYMBOL, "af_eas")
    af_fin = ma_var_iterator(SYMBOL, "af_fin")
    af_nfe = ma_var_iterator(SYMBOL, "af_nfe")
    af_oth = ma_var_iterator(SYMBOL, "af_oth")


class ExacFrequenciesFactory(MacArthurFrequenciesFactoryBase):
    """Factory for ``Exac`` records."""

    class Meta:
        model = Exac

    ac_sas = 0
    an_sas = 323
    hemi_sas = None
    hom_sas = 0
    af_sas = 0.0


class GnomadExomesFactory(MacArthurFrequenciesFactoryBase):
    """Factory for ``GnomadExomes`` records."""

    class Meta:
        model = GnomadExomes

    ac_asj = 0
    ac_sas = 0
    an_asj = 323
    an_sas = 932
    hemi_asj = None
    hemi_sas = None
    hom_asj = 0
    hom_sas = 0
    af_asj = 0.0
    af_sas = 0.0


class GnomadGenomesFactory(MacArthurFrequenciesFactoryBase):
    """Factory for ``GnomadGenomes`` records."""

    class Meta:
        model = GnomadGenomes

    ac_asj = 0
    an_asj = 323
    hemi_asj = None
    hom_asj = 0
    af_asj = 0.0


class ThousandGenomesFactory(factory.django.DjangoModelFactory):
    """Factory for ``ThousandGenomes`` records."""

    class Meta:
        model = ThousandGenomes

    release = small_var_attribute(SYMBOL, "release")
    chromosome = small_var_attribute(SYMBOL, "chromosome")
    position = small_var_iterator(SYMBOL, "position")
    reference = small_var_iterator(SYMBOL, "reference")
    alternative = small_var_iterator(SYMBOL, "alternative")

    ac = 3
    an = 5008
    het = 3
    hom = 0
    af = 0.000058
    af_afr = 0.0
    af_amr = 0.0054
    af_eas = 0.0
    af_eur = 0.0
    af_sas = 0.0
