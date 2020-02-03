from django.db import models
from postgres_copy import CopyManager


class Coordinates(models.Model):
    class Meta:
        abstract = True
        # The uniqueness constraint will automatically add an index, no need to create a second.
        unique_together = ("release", "chromosome", "start", "reference", "alternative")

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: Allow bulk import
    objects = CopyManager()


class Exac(Coordinates):
    """Information of the ExAC database."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordiantes - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Allele count
    ac = models.IntegerField(null=True)
    #: Allele count african population
    ac_afr = models.IntegerField(null=True)
    #: Allele count american population
    ac_amr = models.IntegerField(null=True)
    #: Allele count east asian population
    ac_eas = models.IntegerField(null=True)
    #: Allele count finnish population
    ac_fin = models.IntegerField(null=True)
    #: Allele count european (excl. finnish) population
    ac_nfe = models.IntegerField(null=True)
    #: Allele count other populations
    ac_oth = models.IntegerField(null=True)
    #: Allele count south asian population
    ac_sas = models.IntegerField(null=True)
    #: Allele number
    an = models.IntegerField(null=True)
    #: Allele number african population
    an_afr = models.IntegerField(null=True)
    #: Allele number american population
    an_amr = models.IntegerField(null=True)
    #: Allele number east asian population
    an_eas = models.IntegerField(null=True)
    #: Allele number finnish population
    an_fin = models.IntegerField(null=True)
    #: Allele number european (excl. finnish) population
    an_nfe = models.IntegerField(null=True)
    #: Allele number other populations
    an_oth = models.IntegerField(null=True)
    #: Allele number south asian population
    an_sas = models.IntegerField(null=True)
    #: Hemizygous count
    hemi = models.IntegerField(null=True)
    #: Hemizygous count african population
    hemi_afr = models.IntegerField(null=True)
    #: Hemizygous count american population
    hemi_amr = models.IntegerField(null=True)
    #: Hemizygous count east asian population
    hemi_eas = models.IntegerField(null=True)
    #: Hemizygous count finnish population
    hemi_fin = models.IntegerField(null=True)
    #: Hemizygous count european (excl. finnish) population
    hemi_nfe = models.IntegerField(null=True)
    #: Hemizygous count other populations
    hemi_oth = models.IntegerField(null=True)
    #: Hemizygous count south asian population
    hemi_sas = models.IntegerField(null=True)
    #: Homozygous count
    hom = models.IntegerField(null=True)
    #: Homozygous count african population
    hom_afr = models.IntegerField(null=True)
    #: Homozygous count american population
    hom_amr = models.IntegerField(null=True)
    #: Homozygous count east asian population
    hom_eas = models.IntegerField(null=True)
    #: Homozygous count finnish population
    hom_fin = models.IntegerField(null=True)
    #: Homozygous count european (excl. finnish) population
    hom_nfe = models.IntegerField(null=True)
    #: Homozygous count other populations
    hom_oth = models.IntegerField(null=True)
    #: Hemizygous count south asian population
    hom_sas = models.IntegerField(null=True)
    #: Population with maximum frequency among populations
    popmax = models.CharField(max_length=8, null=True)
    #: Allele count of population with maximum frequency
    ac_popmax = models.IntegerField(null=True)
    #: Allele number of population with maximum frequency
    an_popmax = models.IntegerField(null=True)
    #: Allele frequency of population with maximum frequency
    af_popmax = models.FloatField(null=True)
    #: Hemizygous count of population with maximum frequency
    hemi_popmax = models.IntegerField(null=True)
    #: Homozygous count of population with maximum frequency
    hom_popmax = models.IntegerField(null=True)
    #: Allele frequency
    af = models.FloatField(null=True)
    #: Allele frequency african population
    af_afr = models.FloatField(null=True)
    #: Allele frequency american population
    af_amr = models.FloatField(null=True)
    #: Allele frequency east asian population
    af_eas = models.FloatField(null=True)
    #: Allele frequency finnish population
    af_fin = models.FloatField(null=True)
    #: Allele frequency european (non-finnish) population
    af_nfe = models.FloatField(null=True)
    #: Allele frequency other populations
    af_oth = models.FloatField(null=True)
    #: Allele frequency south asian population
    af_sas = models.FloatField(null=True)

    @property
    def het(self):
        """Heterozygous count"""
        return self.ac - (2 * self.hom) - (self.hemi if self.hemi is not None else 0)

    @property
    def het_afr(self):
        """Heterozygous count african population"""
        return (
            self.ac_afr - (2 * self.hom_afr) - (self.hemi_afr if self.hemi_afr is not None else 0)
        )

    @property
    def het_amr(self):
        """Heterozygous count american population"""
        return (
            self.ac_amr - (2 * self.hom_amr) - (self.hemi_amr if self.hemi_amr is not None else 0)
        )

    @property
    def het_eas(self):
        """Heterozygous count east asian population"""
        return (
            self.ac_eas - (2 * self.hom_eas) - (self.hemi_eas if self.hemi_eas is not None else 0)
        )

    @property
    def het_fin(self):
        """Heterozygous count finnish population"""
        return (
            self.ac_fin - (2 * self.hom_fin) - (self.hemi_fin if self.hemi_fin is not None else 0)
        )

    @property
    def het_nfe(self):
        """Heterozygous count european (non-finnish) population"""
        return (
            self.ac_nfe - (2 * self.hom_nfe) - (self.hemi_nfe if self.hemi_nfe is not None else 0)
        )

    @property
    def het_oth(self):
        """Heterozygous count other populations"""
        return (
            self.ac_oth - (2 * self.hom_oth) - (self.hemi_oth if self.hemi_oth is not None else 0)
        )

    @property
    def het_sas(self):
        """Heterozygous count south asian population"""
        return (
            self.ac_sas - (2 * self.hom_sas) - (self.hemi_sas if self.hemi_sas is not None else 0)
        )


class GnomadExomes(Coordinates):
    """Information of the gnomAD exomes database."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordiantes - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Allele count
    ac = models.IntegerField(null=True)
    #: Allele count african population
    ac_afr = models.IntegerField(null=True)
    #: Allele count american population
    ac_amr = models.IntegerField(null=True)
    #: Allele count ashkenazi jewish population
    ac_asj = models.IntegerField(null=True)
    #: Allele count east asian population
    ac_eas = models.IntegerField(null=True)
    #: Allele count finnish population
    ac_fin = models.IntegerField(null=True)
    #: Allele count european (excl. finnish) population
    ac_nfe = models.IntegerField(null=True)
    #: Allele count other populations
    ac_oth = models.IntegerField(null=True)
    #: Allele count south asian population
    ac_sas = models.IntegerField(null=True)
    #: Allele number
    an = models.IntegerField(null=True)
    #: Allele number african population
    an_afr = models.IntegerField(null=True)
    #: Allele number american population
    an_amr = models.IntegerField(null=True)
    #: Allele number ashkenazi jewish population
    an_asj = models.IntegerField(null=True)
    #: Allele number east asian population
    an_eas = models.IntegerField(null=True)
    #: Allele number finnish population
    an_fin = models.IntegerField(null=True)
    #: Allele number european (excl. finnish) population
    an_nfe = models.IntegerField(null=True)
    #: Allele number other populations
    an_oth = models.IntegerField(null=True)
    #: Allele number south asian population
    an_sas = models.IntegerField(null=True)
    #: Hemizygous count
    hemi = models.IntegerField(null=True)
    #: Hemizygous count african population
    hemi_afr = models.IntegerField(null=True)
    #: Hemizygous count american population
    hemi_amr = models.IntegerField(null=True)
    #: Hemizygous count ashkenazi jewish population
    hemi_asj = models.IntegerField(null=True)
    #: Hemizygous count east asian population
    hemi_eas = models.IntegerField(null=True)
    #: Hemizygous count finnish population
    hemi_fin = models.IntegerField(null=True)
    #: Hemizygous count european (excl. finnish) population
    hemi_nfe = models.IntegerField(null=True)
    #: Hemizygous count other populations
    hemi_oth = models.IntegerField(null=True)
    #: Hemizygous count south asian population
    hemi_sas = models.IntegerField(null=True)
    #: Homozygous count
    hom = models.IntegerField(null=True)
    #: Homozygous count african population
    hom_afr = models.IntegerField(null=True)
    #: Homozygous count american population
    hom_amr = models.IntegerField(null=True)
    #: Homozygous count ashkenazi jewish population
    hom_asj = models.IntegerField(null=True)
    #: Homozygous count east asian population
    hom_eas = models.IntegerField(null=True)
    #: Homozygous count finnish population
    hom_fin = models.IntegerField(null=True)
    #: Homozygous count european (excl. finnish) population
    hom_nfe = models.IntegerField(null=True)
    #: Homozygous count other populations
    hom_oth = models.IntegerField(null=True)
    #: Hemizygous count south asian population
    hom_sas = models.IntegerField(null=True)
    #: Population with maximum frequency among populations
    popmax = models.CharField(max_length=8, null=True)
    #: Allele count of population with maximum frequency
    ac_popmax = models.IntegerField(null=True)
    #: Allele number of population with maximum frequency
    an_popmax = models.IntegerField(null=True)
    #: Allele frequency of population with maximum frequency
    af_popmax = models.FloatField(null=True)
    #: Hemizygous count of population with maximum frequency
    hemi_popmax = models.IntegerField(null=True)
    #: Homozygous count of population with maximum frequency
    hom_popmax = models.IntegerField(null=True)
    #: Allele frequency
    af = models.FloatField(null=True)
    #: Allele frequency african population
    af_afr = models.FloatField(null=True)
    #: Allele frequency american population
    af_amr = models.FloatField(null=True)
    #: Allele frequency ashkenazi jewish population
    af_asj = models.FloatField(null=True)
    #: Allele frequency east asian population
    af_eas = models.FloatField(null=True)
    #: Allele frequency finnish population
    af_fin = models.FloatField(null=True)
    #: Allele frequency european (non-finnish) population
    af_nfe = models.FloatField(null=True)
    #: Allele frequency other populations
    af_oth = models.FloatField(null=True)
    #: Allele frequency south asian population
    af_sas = models.FloatField(null=True)
    #: Controls for allele count
    controls_ac = models.IntegerField(null=True)
    #: Controls for allele number
    controls_an = models.IntegerField(null=True)
    #: Controls for allele frequency
    controls_af = models.FloatField(null=True)
    #: Controls for hemizygous count
    controls_hemi = models.IntegerField(null=True)
    #: Controls for homozygous count
    controls_hom = models.IntegerField(null=True)
    #: Controls for allele count african population
    controls_ac_afr = models.IntegerField(null=True)
    #: Controls for allele number african population
    controls_an_afr = models.IntegerField(null=True)
    #: Controls for allele frequency african population
    controls_af_afr = models.FloatField(null=True)
    #: Controls for hemizygous count african population
    controls_hemi_afr = models.IntegerField(null=True)
    #: Controls for homozygous count african population
    controls_hom_afr = models.IntegerField(null=True)
    #: Controls for allele count american population
    controls_ac_amr = models.IntegerField(null=True)
    #: Controls for allele number american population
    controls_an_amr = models.IntegerField(null=True)
    #: Controls for allele frequency american population
    controls_af_amr = models.FloatField(null=True)
    #: Controls for hemizygous count american population
    controls_hemi_amr = models.IntegerField(null=True)
    #: Controls for homozygous count american population
    controls_hom_amr = models.IntegerField(null=True)
    #: Controls for allele count ashkenazi jewish population
    controls_ac_asj = models.IntegerField(null=True)
    #: Controls for allele number ashkenazi jewish population
    controls_an_asj = models.IntegerField(null=True)
    #: Controls for allele frequency ashkenazi jewish population
    controls_af_asj = models.FloatField(null=True)
    #: Controls for hemizygous count ashkenazi jewish population
    controls_hemi_asj = models.IntegerField(null=True)
    #: Controls for homozygous count ashkenazi jewish population
    controls_hom_asj = models.IntegerField(null=True)
    #: Controls for allele count east asian population
    controls_ac_eas = models.IntegerField(null=True)
    #: Controls for allele number east asian population
    controls_an_eas = models.IntegerField(null=True)
    #: Controls for allele frequency east asian population
    controls_af_eas = models.FloatField(null=True)
    #: Controls for hemizygous count east asian population
    controls_hemi_eas = models.IntegerField(null=True)
    #: Controls for hemizygous count east asian population
    controls_hom_eas = models.IntegerField(null=True)
    #: Controls for allele count finnish population
    controls_ac_fin = models.IntegerField(null=True)
    #: Controls for allele number finnish population
    controls_an_fin = models.IntegerField(null=True)
    #: Controls for allele frequency finnish population
    controls_af_fin = models.FloatField(null=True)
    #: Controls for hemizygous count finnish population
    controls_hemi_fin = models.IntegerField(null=True)
    #: Controls for hemizygous count finnish population
    controls_hom_fin = models.IntegerField(null=True)
    #: Controls for allele count european (excl. finnish) population
    controls_ac_nfe = models.IntegerField(null=True)
    #: Controls for allele number european (excl. finnish) population
    controls_an_nfe = models.IntegerField(null=True)
    #: Controls for allele frequency european (excl. finnish) population
    controls_af_nfe = models.FloatField(null=True)
    #: Controls for hemizygous count european (excl. finnish) population
    controls_hemi_nfe = models.IntegerField(null=True)
    #: Controls for hemizygous count european (excl. finnish) population
    controls_hom_nfe = models.IntegerField(null=True)
    #: Controls for allele count other population
    controls_ac_oth = models.IntegerField(null=True)
    #: Controls for allele number other population
    controls_an_oth = models.IntegerField(null=True)
    #: Controls for allele frequency other population
    controls_af_oth = models.FloatField(null=True)
    #: Controls for hemizygous count other population
    controls_hemi_oth = models.IntegerField(null=True)
    #: Controls for hemizygous count other population
    controls_hom_oth = models.IntegerField(null=True)
    #: Controls for allele count south asian population
    controls_ac_sas = models.IntegerField(null=True)
    #: Controls for allele number south asian population
    controls_an_sas = models.IntegerField(null=True)
    #: Controls for allele frequency south asian population
    controls_af_sas = models.FloatField(null=True)
    #: Controls for hemizygous count south asian population
    controls_hemi_sas = models.IntegerField(null=True)
    #: Controls for hemizygous count south asian population
    controls_hom_sas = models.IntegerField(null=True)
    #: Controls for population with maximum frequency among populations
    controls_popmax = models.CharField(max_length=8, null=True)
    #: Controls for allele count of population with maximum frequency
    controls_ac_popmax = models.IntegerField(null=True)
    #: Controls for allele number of population with maximum frequency
    controls_an_popmax = models.IntegerField(null=True)
    #: Controls for allele frequency of population with maximum frequency
    controls_af_popmax = models.FloatField(null=True)
    #: Controls for hemizygous count of population with maximum frequency
    controls_hemi_popmax = models.IntegerField(null=True)
    #: Controls for homozygous count of population with maximum frequency
    controls_hom_popmax = models.IntegerField(null=True)

    @property
    def het(self):
        """Heterozygous count"""
        try:
            return self.ac - (2 * self.hom) - (self.hemi if self.hemi is not None else 0)
        except TypeError:
            return 0

    @property
    def het_afr(self):
        """Heterozygous count african population"""
        try:
            return (
                self.ac_afr
                - (2 * self.hom_afr)
                - (self.hemi_afr if self.hemi_afr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_amr(self):
        """Heterozygous count american population"""
        try:
            return (
                self.ac_amr
                - (2 * self.hom_amr)
                - (self.hemi_amr if self.hemi_amr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_asj(self):
        """Heterozygous count ashkenazi jewish population"""
        try:
            return (
                self.ac_asj
                - (2 * self.hom_asj)
                - (self.hemi_asj if self.hemi_asj is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_eas(self):
        """Heterozygous count east asian population"""
        try:
            return (
                self.ac_eas
                - (2 * self.hom_eas)
                - (self.hemi_eas if self.hemi_eas is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_fin(self):
        """Heterozygous count finnish population"""
        try:
            return (
                self.ac_fin
                - (2 * self.hom_fin)
                - (self.hemi_fin if self.hemi_fin is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_nfe(self):
        """Heterozygous count european (non-finnish) population"""
        try:
            return (
                self.ac_nfe
                - (2 * self.hom_nfe)
                - (self.hemi_nfe if self.hemi_nfe is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_oth(self):
        """Heterozygous count other populations"""
        try:
            return (
                self.ac_oth
                - (2 * self.hom_oth)
                - (self.hemi_oth if self.hemi_oth is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_sas(self):
        """Heterozygous count south asian population"""
        try:
            return (
                self.ac_sas
                - (2 * self.hom_sas)
                - (self.hemi_sas if self.hemi_sas is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het(self):
        """Controls for heterozygous count"""
        try:
            return (
                self.controls_ac
                - (2 * self.controls_hom)
                - (self.controls_hemi if self.controls_hemi is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_afr(self):
        """Controls for heterozygous count african population"""
        try:
            return (
                self.controls_ac_afr
                - (2 * self.controls_hom_afr)
                - (self.controls_hemi_afr if self.controls_hemi_afr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_amr(self):
        """Controls for heterozygous count american population"""
        try:
            return (
                self.controls_ac_amr
                - (2 * self.controls_hom_amr)
                - (self.controls_hemi_amr if self.controls_hemi_amr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_asj(self):
        """Controls for heterozygous count ashkenazi jewish population"""
        try:
            return (
                self.controls_ac_asj
                - (2 * self.controls_hom_asj)
                - (self.controls_hemi_asj if self.controls_hemi_asj is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_eas(self):
        """Controls for heterozygous count east asian population"""
        try:
            return (
                self.controls_ac_eas
                - (2 * self.controls_hom_eas)
                - (self.controls_hemi_eas if self.controls_hemi_eas is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_fin(self):
        """Controls for heterozygous count finnish population"""
        try:
            return (
                self.controls_ac_fin
                - (2 * self.controls_hom_fin)
                - (self.controls_hemi_fin if self.controls_hemi_fin is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_nfe(self):
        """Controls for heterozygous count european (non-finnish) population"""
        try:
            return (
                self.controls_ac_nfe
                - (2 * self.controls_hom_nfe)
                - (self.controls_hemi_nfe if self.controls_hemi_nfe is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_oth(self):
        """Controls for heterozygous count other populations"""
        try:
            return (
                self.controls_ac_oth
                - (2 * self.controls_hom_oth)
                - (self.controls_hemi_oth if self.controls_hemi_oth is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_sas(self):
        """Controls for heterozygous count south asian population"""
        try:
            return (
                self.controls_ac_sas
                - (2 * self.controls_hom_sas)
                - (self.controls_hemi_sas if self.controls_hemi_sas is not None else 0)
            )
        except TypeError:
            return 0


class GnomadGenomes(Coordinates):
    """Information of the gnomad genomes database."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordiantes - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Allele count
    ac = models.IntegerField(null=True)
    #: Allele count african population
    ac_afr = models.IntegerField(null=True)
    #: Allele count american population
    ac_amr = models.IntegerField(null=True)
    #: Allele count ashkenazi jewish population
    ac_asj = models.IntegerField(null=True)
    #: Allele count east asian population
    ac_eas = models.IntegerField(null=True)
    #: Allele count finnish population
    ac_fin = models.IntegerField(null=True)
    #: Allele count european (excl. finnish) population
    ac_nfe = models.IntegerField(null=True)
    #: Allele count other populations
    ac_oth = models.IntegerField(null=True)
    #: Allele number
    an = models.IntegerField(null=True)
    #: Allele number african population
    an_afr = models.IntegerField(null=True)
    #: Allele number american population
    an_amr = models.IntegerField(null=True)
    #: Allele number ashkenazi jewish population
    an_asj = models.IntegerField(null=True)
    #: Allele number east asian population
    an_eas = models.IntegerField(null=True)
    #: Allele number finnish population
    an_fin = models.IntegerField(null=True)
    #: Allele number european (excl. finnish) population
    an_nfe = models.IntegerField(null=True)
    #: Allele number other populations
    an_oth = models.IntegerField(null=True)
    #: Hemizygous count
    hemi = models.IntegerField(null=True)
    #: Hemizygous count african population
    hemi_afr = models.IntegerField(null=True)
    #: Hemizygous count american population
    hemi_amr = models.IntegerField(null=True)
    #: Hemizygous count ashkenazi jewish population
    hemi_asj = models.IntegerField(null=True)
    #: Hemizygous count east asian population
    hemi_eas = models.IntegerField(null=True)
    #: Hemizygous count finnish population
    hemi_fin = models.IntegerField(null=True)
    #: Hemizygous count european (excl. finnish) population
    hemi_nfe = models.IntegerField(null=True)
    #: Hemizygous count other populations
    hemi_oth = models.IntegerField(null=True)
    #: Homozygous count
    hom = models.IntegerField(null=True)
    #: Homozygous count african population
    hom_afr = models.IntegerField(null=True)
    #: Homozygous count american population
    hom_amr = models.IntegerField(null=True)
    #: Homozygous count ashkenazi jewish population
    hom_asj = models.IntegerField(null=True)
    #: Homozygous count east asian population
    hom_eas = models.IntegerField(null=True)
    #: Homozygous count finnish population
    hom_fin = models.IntegerField(null=True)
    #: Homozygous count european (excl. finnish) population
    hom_nfe = models.IntegerField(null=True)
    #: Homozygous count other populations
    hom_oth = models.IntegerField(null=True)
    #: Population with maximum frequency among populations
    popmax = models.CharField(max_length=8, null=True)
    #: Allele count of population with maximum frequency
    ac_popmax = models.IntegerField(null=True)
    #: Allele number of population with maximum frequency
    an_popmax = models.IntegerField(null=True)
    #: Allele frequency of population with maximum frequency
    af_popmax = models.FloatField(null=True)
    #: Hemizygous count of population with maximum frequency
    hemi_popmax = models.IntegerField(null=True)
    #: Homozygous count of population with maximum frequency
    hom_popmax = models.IntegerField(null=True)
    #: Allele frequency
    af = models.FloatField(null=True)
    #: Allele frequency african population
    af_afr = models.FloatField(null=True)
    #: Allele frequency american population
    af_amr = models.FloatField(null=True)
    #: Allele frequency ashkenazi jewish population
    af_asj = models.FloatField(null=True)
    #: Allele frequency east asian population
    af_eas = models.FloatField(null=True)
    #: Allele frequency finnish population
    af_fin = models.FloatField(null=True)
    #: Allele frequency european (non-finnish) population
    af_nfe = models.FloatField(null=True)
    #: Allele frequency other populations
    af_oth = models.FloatField(null=True)
    #: Controls for allele count
    controls_ac = models.IntegerField(null=True)
    #: Controls for allele number
    controls_an = models.IntegerField(null=True)
    #: Controls for allele frequency
    controls_af = models.FloatField(null=True)
    #: Controls for hemizygous count
    controls_hemi = models.IntegerField(null=True)
    #: Controls for homozygous count
    controls_hom = models.IntegerField(null=True)
    #: Controls for allele count african population
    controls_ac_afr = models.IntegerField(null=True)
    #: Controls for allele number african population
    controls_an_afr = models.IntegerField(null=True)
    #: Controls for allele frequency african population
    controls_af_afr = models.FloatField(null=True)
    #: Controls for hemizygous count african population
    controls_hemi_afr = models.IntegerField(null=True)
    #: Controls for homozygous count african population
    controls_hom_afr = models.IntegerField(null=True)
    #: Controls for allele count american population
    controls_ac_amr = models.IntegerField(null=True)
    #: Controls for allele number american population
    controls_an_amr = models.IntegerField(null=True)
    #: Controls for allele frequency american population
    controls_af_amr = models.FloatField(null=True)
    #: Controls for hemizygous count american population
    controls_hemi_amr = models.IntegerField(null=True)
    #: Controls for homozygous count american population
    controls_hom_amr = models.IntegerField(null=True)
    #: Controls for allele count ashkenazi jewish population
    controls_ac_asj = models.IntegerField(null=True)
    #: Controls for allele number ashkenazi jewish population
    controls_an_asj = models.IntegerField(null=True)
    #: Controls for allele frequency ashkenazi jewish population
    controls_af_asj = models.FloatField(null=True)
    #: Controls for hemizygous count ashkenazi jewish population
    controls_hemi_asj = models.IntegerField(null=True)
    #: Controls for homozygous count ashkenazi jewish population
    controls_hom_asj = models.IntegerField(null=True)
    #: Controls for allele count east asian population
    controls_ac_eas = models.IntegerField(null=True)
    #: Controls for allele number east asian population
    controls_an_eas = models.IntegerField(null=True)
    #: Controls for allele frequency east asian population
    controls_af_eas = models.FloatField(null=True)
    #: Controls for hemizygous count east asian population
    controls_hemi_eas = models.IntegerField(null=True)
    #: Controls for hemizygous count east asian population
    controls_hom_eas = models.IntegerField(null=True)
    #: Controls for allele count finnish population
    controls_ac_fin = models.IntegerField(null=True)
    #: Controls for allele number finnish population
    controls_an_fin = models.IntegerField(null=True)
    #: Controls for allele frequency finnish population
    controls_af_fin = models.FloatField(null=True)
    #: Controls for hemizygous count finnish population
    controls_hemi_fin = models.IntegerField(null=True)
    #: Controls for hemizygous count finnish population
    controls_hom_fin = models.IntegerField(null=True)
    #: Controls for allele count european (excl. finnish) population
    controls_ac_nfe = models.IntegerField(null=True)
    #: Controls for allele number european (excl. finnish) population
    controls_an_nfe = models.IntegerField(null=True)
    #: Controls for allele frequency european (excl. finnish) population
    controls_af_nfe = models.FloatField(null=True)
    #: Controls for hemizygous count european (excl. finnish) population
    controls_hemi_nfe = models.IntegerField(null=True)
    #: Controls for hemizygous count european (excl. finnish) population
    controls_hom_nfe = models.IntegerField(null=True)
    #: Controls for allele count other population
    controls_ac_oth = models.IntegerField(null=True)
    #: Controls for allele number other population
    controls_an_oth = models.IntegerField(null=True)
    #: Controls for allele frequency other population
    controls_af_oth = models.FloatField(null=True)
    #: Controls for hemizygous count other population
    controls_hemi_oth = models.IntegerField(null=True)
    #: Controls for hemizygous count other population
    controls_hom_oth = models.IntegerField(null=True)
    #: Controls for population with maximum frequency among populations
    controls_popmax = models.CharField(max_length=8, null=True)
    #: Controls for allele count of population with maximum frequency
    controls_ac_popmax = models.IntegerField(null=True)
    #: Controls for allele number of population with maximum frequency
    controls_an_popmax = models.IntegerField(null=True)
    #: Controls for allele frequency of population with maximum frequency
    controls_af_popmax = models.FloatField(null=True)
    #: Controls for hemizygous count of population with maximum frequency
    controls_hemi_popmax = models.IntegerField(null=True)
    #: Controls for homozygous count of population with maximum frequency
    controls_hom_popmax = models.IntegerField(null=True)

    @property
    def het(self):
        """Heterozygous count"""
        try:
            return self.ac - (2 * self.hom) - (self.hemi if self.hemi is not None else 0)
        except TypeError:
            return 0

    @property
    def het_afr(self):
        """Heterozygous count african population"""
        try:
            return (
                self.ac_afr
                - (2 * self.hom_afr)
                - (self.hemi_afr if self.hemi_afr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_amr(self):
        """Heterozygous count american population"""
        try:
            return (
                self.ac_amr
                - (2 * self.hom_amr)
                - (self.hemi_amr if self.hemi_amr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_asj(self):
        """Heterozygous count ashkenazi jewish population"""
        try:
            return (
                self.ac_asj
                - (2 * self.hom_asj)
                - (self.hemi_asj if self.hemi_asj is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_eas(self):
        """Heterozygous count east asian population"""
        try:
            return (
                self.ac_eas
                - (2 * self.hom_eas)
                - (self.hemi_eas if self.hemi_eas is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_fin(self):
        """Heterozygous count finnish population"""
        try:
            return (
                self.ac_fin
                - (2 * self.hom_fin)
                - (self.hemi_fin if self.hemi_fin is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_nfe(self):
        """Heterozygous count european (non-finnish) population"""
        try:
            return (
                self.ac_nfe
                - (2 * self.hom_nfe)
                - (self.hemi_nfe if self.hemi_nfe is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def het_oth(self):
        """Heterozygous count other populations"""
        try:
            return (
                self.ac_oth
                - (2 * self.hom_oth)
                - (self.hemi_oth if self.hemi_oth is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het(self):
        """Controls for heterozygous count"""
        try:
            return (
                self.controls_ac
                - (2 * self.controls_hom)
                - (self.controls_hemi if self.controls_hemi is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_afr(self):
        """Controls for heterozygous count african population"""
        try:
            return (
                self.controls_ac_afr
                - (2 * self.controls_hom_afr)
                - (self.controls_hemi_afr if self.controls_hemi_afr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_amr(self):
        """Controls for heterozygous count american population"""
        try:
            return (
                self.controls_ac_amr
                - (2 * self.controls_hom_amr)
                - (self.controls_hemi_amr if self.controls_hemi_amr is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_asj(self):
        """Controls for heterozygous count ashkenazi jewish population"""
        try:
            return (
                self.controls_ac_asj
                - (2 * self.controls_hom_asj)
                - (self.controls_hemi_asj if self.controls_hemi_asj is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_eas(self):
        """Controls for heterozygous count east asian population"""
        try:
            return (
                self.controls_ac_eas
                - (2 * self.controls_hom_eas)
                - (self.controls_hemi_eas if self.controls_hemi_eas is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_fin(self):
        """Controls for heterozygous count finnish population"""
        try:
            return (
                self.controls_ac_fin
                - (2 * self.controls_hom_fin)
                - (self.controls_hemi_fin if self.controls_hemi_fin is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_nfe(self):
        """Controls for heterozygous count european (non-finnish) population"""
        try:
            return (
                self.controls_ac_nfe
                - (2 * self.controls_hom_nfe)
                - (self.controls_hemi_nfe if self.controls_hemi_nfe is not None else 0)
            )
        except TypeError:
            return 0

    @property
    def controls_het_oth(self):
        """Controls for heterozygous count other populations"""
        try:
            return (
                self.controls_ac_oth
                - (2 * self.controls_hom_oth)
                - (self.controls_hemi_oth if self.controls_hemi_oth is not None else 0)
            )
        except TypeError:
            return 0


class ThousandGenomes(Coordinates):
    """Information of the thousand genomes database."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordiantes - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Allele count
    ac = models.IntegerField(null=True)
    #: Allele number
    an = models.IntegerField(null=True)
    #: Heterozygous count
    het = models.IntegerField(null=True)
    #: Homozygous count
    hom = models.IntegerField(null=True)
    #: Allele frequency
    af = models.FloatField(null=True)
    #: Allele frequency african population
    af_afr = models.FloatField(null=True)
    #: Allele frequency american population
    af_amr = models.FloatField(null=True)
    #: Allele frequency east asian population
    af_eas = models.FloatField(null=True)
    #: Allele frequency european population
    af_eur = models.FloatField(null=True)
    #: Allele frequency south asian population
    af_sas = models.FloatField(null=True)


class HelixMtDb(Coordinates):
    # Allele count, i.e. homoplasmy + heteroplasmy
    ac = models.IntegerField()
    # Allele number, i.e. number of sequenced individuals (stated in paper)
    an = models.IntegerField()
    # Allele frequency, i.e. ac/an
    af = models.FloatField()
    # Heteroplasmy
    ac_het = models.IntegerField()
    # Heteroplasmy mean
    ac_het_mean = models.FloatField(null=True)
    # Heteroplasmy standard deviation
    ac_het_stdev = models.FloatField(null=True)
    # Heteroplasmy min value
    ac_het_min = models.FloatField(null=True)
    # Heteroplasmy max value
    ac_het_max = models.FloatField(null=True)


class MtDb(Coordinates):
    # Allele count
    ac = models.IntegerField()
    # Allele number, derived from TSV
    an = models.IntegerField()
    # Allele frequency, i.e. ac/an
    af = models.FloatField()
    # Location
    location = models.CharField(max_length=32, null=True)
    # Codon
    codon = models.IntegerField(null=True)
    # Position in codon
    position = models.IntegerField(null=True)
    # Amino acid change
    aa_change = models.CharField(max_length=32, null=True)
    # Amino acid change is synonymous?
    synonymous = models.NullBooleanField()


class Mitomap(Coordinates):
    # Allele count
    ac = models.IntegerField()
    # Allele number, i.e. number of sequenced individuals (available on web page)
    an = models.IntegerField()
    # Allele frequency, i.e. ac/an
    af = models.FloatField()


#: Information about frequency databases used in ``FrequencyQuery``.
FREQUENCY_DB_INFO = {
    "gnomadexomes": {
        "model": GnomadExomes,
        "populations": ("afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas"),
    },
    "gnomadgenomes": {
        "model": GnomadGenomes,
        "populations": ("afr", "amr", "asj", "eas", "fin", "nfe", "oth"),
    },
    "exac": {"model": Exac, "populations": ("afr", "amr", "eas", "fin", "nfe", "oth", "sas")},
    "thousandgenomes": {
        "model": ThousandGenomes,
        "populations": ("afr", "amr", "eas", "eur", "sas"),
    },
}

MT_DB_INFO = {
    "MITOMAP": Mitomap,
    "mtDB": MtDb,
    "HelixMTdb": HelixMtDb,
}
