"""Factory Boy factory classes for ``frequencies``."""

import factory

from ..models import Exac, GnomadExomes, GnomadGenomes, ThousandGenomes


class MacArthurFrequenciesFactoryBase(factory.django.DjangoModelFactory):
    """Base class for the ``frequencies``'s from ExAC and gnomAD."""

    class Meta:
        abstract = True

    release = "GRCh37"
    chromosome = factory.Iterator((list(map(str, range(1, 23))) + ["X", "Y"]))
    position = factory.Sequence(lambda n: n * 100)
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")

    ac = 1
    ac_amr = 0
    ac_eas = 0
    ac_fin = 0
    ac_nfe = 0
    ac_oth = 0
    an = None
    an_afr = 8726
    an_amr = 838
    an_eas = 1620
    an_fin = 3464
    an_nfe = 14996
    an_oth = 982
    hemi = None
    hemi_afr = None
    hemi_amr = None
    hemi_eas = None
    hemi_fin = None
    hemi_nfe = None
    hemi_oth = None
    hom = 0
    hom_afr = 0
    hom_amr = 0
    hom_eas = 0
    hom_fin = 0
    hom_nfe = 0
    hom_oth = 0
    popmax = "AFR"
    ac_popmax = 1
    an_popmax = 8726
    af_popmax = 0.0001146
    hemi_popmax = None
    hom_popmax = 0
    af = None
    af_afr = 0.0001146
    af_amr = 0.0
    af_eas = 0.0
    af_fin = 0.0
    af_nfe = 0.0
    af_oth = 0.0


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

    release = "GRCh37"
    chromosome = factory.Iterator((list(map(str, range(1, 23))) + ["X", "Y"]))
    position = factory.Sequence(lambda n: n * 100)
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")

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
