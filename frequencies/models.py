from django.db import models
from postgres_copy import CopyManager


class Exac(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    ac = models.IntegerField(null=True)
    ac_afr = models.IntegerField(null=True)
    ac_amr = models.IntegerField(null=True)
    ac_eas = models.IntegerField(null=True)
    ac_fin = models.IntegerField(null=True)
    ac_nfe = models.IntegerField(null=True)
    ac_oth = models.IntegerField(null=True)
    ac_sas = models.IntegerField(null=True)
    an = models.IntegerField(null=True)
    an_afr = models.IntegerField(null=True)
    an_amr = models.IntegerField(null=True)
    an_eas = models.IntegerField(null=True)
    an_fin = models.IntegerField(null=True)
    an_nfe = models.IntegerField(null=True)
    an_oth = models.IntegerField(null=True)
    an_sas = models.IntegerField(null=True)
    hemi = models.IntegerField(null=True)
    hemi_afr = models.IntegerField(null=True)
    hemi_amr = models.IntegerField(null=True)
    hemi_eas = models.IntegerField(null=True)
    hemi_fin = models.IntegerField(null=True)
    hemi_nfe = models.IntegerField(null=True)
    hemi_oth = models.IntegerField(null=True)
    hemi_sas = models.IntegerField(null=True)
    hom = models.IntegerField(null=True)
    hom_afr = models.IntegerField(null=True)
    hom_amr = models.IntegerField(null=True)
    hom_eas = models.IntegerField(null=True)
    hom_fin = models.IntegerField(null=True)
    hom_nfe = models.IntegerField(null=True)
    hom_oth = models.IntegerField(null=True)
    hom_sas = models.IntegerField(null=True)
    popmax = models.CharField(max_length=8, null=True)
    ac_popmax = models.IntegerField(null=True)
    an_popmax = models.IntegerField(null=True)
    af_popmax = models.FloatField(null=True)
    hemi_popmax = models.IntegerField(null=True)
    hom_popmax = models.IntegerField(null=True)
    af = models.FloatField(null=True)
    af_afr = models.FloatField(null=True)
    af_amr = models.FloatField(null=True)
    af_eas = models.FloatField(null=True)
    af_fin = models.FloatField(null=True)
    af_nfe = models.FloatField(null=True)
    af_oth = models.FloatField(null=True)
    af_sas = models.FloatField(null=True)
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
        )
        indexes = [
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                ]
            )
        ]


class GnomadExomes(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    ac = models.IntegerField(null=True)
    ac_afr = models.IntegerField(null=True)
    ac_amr = models.IntegerField(null=True)
    ac_asj = models.IntegerField(null=True)
    ac_eas = models.IntegerField(null=True)
    ac_fin = models.IntegerField(null=True)
    ac_nfe = models.IntegerField(null=True)
    ac_oth = models.IntegerField(null=True)
    ac_sas = models.IntegerField(null=True)
    an = models.IntegerField(null=True)
    an_afr = models.IntegerField(null=True)
    an_amr = models.IntegerField(null=True)
    an_asj = models.IntegerField(null=True)
    an_eas = models.IntegerField(null=True)
    an_fin = models.IntegerField(null=True)
    an_nfe = models.IntegerField(null=True)
    an_oth = models.IntegerField(null=True)
    an_sas = models.IntegerField(null=True)
    hemi = models.IntegerField(null=True)
    hemi_afr = models.IntegerField(null=True)
    hemi_amr = models.IntegerField(null=True)
    hemi_asj = models.IntegerField(null=True)
    hemi_eas = models.IntegerField(null=True)
    hemi_fin = models.IntegerField(null=True)
    hemi_nfe = models.IntegerField(null=True)
    hemi_oth = models.IntegerField(null=True)
    hemi_sas = models.IntegerField(null=True)
    hom = models.IntegerField(null=True)
    hom_afr = models.IntegerField(null=True)
    hom_amr = models.IntegerField(null=True)
    hom_asj = models.IntegerField(null=True)
    hom_eas = models.IntegerField(null=True)
    hom_fin = models.IntegerField(null=True)
    hom_nfe = models.IntegerField(null=True)
    hom_oth = models.IntegerField(null=True)
    hom_sas = models.IntegerField(null=True)
    popmax = models.CharField(max_length=8, null=True)
    ac_popmax = models.IntegerField(null=True)
    an_popmax = models.IntegerField(null=True)
    af_popmax = models.FloatField(null=True)
    hemi_popmax = models.IntegerField(null=True)
    hom_popmax = models.IntegerField(null=True)
    af = models.FloatField(null=True)
    af_afr = models.FloatField(null=True)
    af_amr = models.FloatField(null=True)
    af_asj = models.FloatField(null=True)
    af_eas = models.FloatField(null=True)
    af_fin = models.FloatField(null=True)
    af_nfe = models.FloatField(null=True)
    af_oth = models.FloatField(null=True)
    af_sas = models.FloatField(null=True)
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
        )
        indexes = [
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                ]
            )
        ]


class GnomadGenomes(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    ac = models.IntegerField(null=True)
    ac_afr = models.IntegerField(null=True)
    ac_amr = models.IntegerField(null=True)
    ac_asj = models.IntegerField(null=True)
    ac_eas = models.IntegerField(null=True)
    ac_fin = models.IntegerField(null=True)
    ac_nfe = models.IntegerField(null=True)
    ac_oth = models.IntegerField(null=True)
    an = models.IntegerField(null=True)
    an_afr = models.IntegerField(null=True)
    an_amr = models.IntegerField(null=True)
    an_asj = models.IntegerField(null=True)
    an_eas = models.IntegerField(null=True)
    an_fin = models.IntegerField(null=True)
    an_nfe = models.IntegerField(null=True)
    an_oth = models.IntegerField(null=True)
    hemi = models.IntegerField(null=True)
    hemi_afr = models.IntegerField(null=True)
    hemi_amr = models.IntegerField(null=True)
    hemi_asj = models.IntegerField(null=True)
    hemi_eas = models.IntegerField(null=True)
    hemi_fin = models.IntegerField(null=True)
    hemi_nfe = models.IntegerField(null=True)
    hemi_oth = models.IntegerField(null=True)
    hom = models.IntegerField(null=True)
    hom_afr = models.IntegerField(null=True)
    hom_amr = models.IntegerField(null=True)
    hom_asj = models.IntegerField(null=True)
    hom_eas = models.IntegerField(null=True)
    hom_fin = models.IntegerField(null=True)
    hom_nfe = models.IntegerField(null=True)
    hom_oth = models.IntegerField(null=True)
    popmax = models.CharField(max_length=8, null=True)
    ac_popmax = models.IntegerField(null=True)
    an_popmax = models.IntegerField(null=True)
    af_popmax = models.FloatField(null=True)
    hemi_popmax = models.IntegerField(null=True)
    hom_popmax = models.IntegerField(null=True)
    af = models.FloatField(null=True)
    af_afr = models.FloatField(null=True)
    af_amr = models.FloatField(null=True)
    af_asj = models.FloatField(null=True)
    af_eas = models.FloatField(null=True)
    af_fin = models.FloatField(null=True)
    af_nfe = models.FloatField(null=True)
    af_oth = models.FloatField(null=True)
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
        )
        indexes = [
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                ]
            )
        ]


class ThousandGenomes(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    ac = models.IntegerField(null=True)
    an = models.IntegerField(null=True)
    het = models.IntegerField(null=True)
    hom = models.IntegerField(null=True)
    af = models.FloatField(null=True)
    af_afr = models.FloatField(null=True)
    af_amr = models.FloatField(null=True)
    af_eas = models.FloatField(null=True)
    af_eur = models.FloatField(null=True)
    af_sas = models.FloatField(null=True)
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
        )
        indexes = [
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                ]
            )
        ]

