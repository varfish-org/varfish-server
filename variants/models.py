from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from projectroles.models import Project
from postgres_copy import CopyManager
import uuid as uuid_object


class SmallVariant(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    var_type = models.CharField(max_length=8)
    case_id = models.IntegerField()
    genotype = JSONField()
    in_clinvar = models.NullBooleanField()
    exac_frequency = models.FloatField(null=True)
    exac_homozygous = models.IntegerField(null=True)
    exac_heterozygous = models.IntegerField(null=True)
    exac_hemizygous = models.IntegerField(null=True)
    thousand_genomes_frequency = models.FloatField(null=True)
    thousand_genomes_homozygous = models.IntegerField(null=True)
    thousand_genomes_heterozygous = models.IntegerField(null=True)
    thousand_genomes_hemizygous = models.IntegerField(null=True)
    gnomad_exomes_frequency = models.FloatField(null=True)
    gnomad_exomes_homozygous = models.IntegerField(null=True)
    gnomad_exomes_heterozygous = models.IntegerField(null=True)
    gnomad_exomes_hemizygous = models.IntegerField(null=True)
    gnomad_genomes_frequency = models.FloatField(null=True)
    gnomad_genomes_homozygous = models.IntegerField(null=True)
    gnomad_genomes_heterozygous = models.IntegerField(null=True)
    gnomad_genomes_hemizygous = models.IntegerField(null=True)
    refseq_gene_id = models.CharField(max_length=16, null=True)
    refseq_transcript_id = models.CharField(max_length=16, null=True)
    refseq_transcript_coding = models.NullBooleanField()
    refseq_hgvs_c = models.CharField(max_length=512, null=True)
    refseq_hgvs_p = models.CharField(max_length=512, null=True)
    refseq_effect = ArrayField(models.CharField(max_length=64), null=True)
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    ensembl_transcript_id = models.CharField(max_length=16, null=True)
    ensembl_transcript_coding = models.NullBooleanField()
    ensembl_hgvs_c = models.CharField(max_length=512, null=True)
    ensembl_hgvs_p = models.CharField(max_length=512, null=True)
    ensembl_effect = ArrayField(models.CharField(max_length=64, null=True))
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
            "case_id",
            "ensembl_gene_id",
            "refseq_gene_id",
        )
        indexes = [
            # index for base query
            models.Index(
                fields=[
                    "exac_frequency",
                    "gnomad_exomes_frequency",
                    "gnomad_genomes_frequency",
                    "thousand_genomes_frequency",
                    "exac_homozygous",
                    "gnomad_exomes_homozygous",
                    "gnomad_genomes_homozygous",
                    "thousand_genomes_homozygous",
                    "refseq_effect",
                ]
            ),
            models.Index(
                fields=[
                    "exac_frequency",
                    "gnomad_exomes_frequency",
                    "gnomad_genomes_frequency",
                    "thousand_genomes_frequency",
                    "exac_homozygous",
                    "gnomad_exomes_homozygous",
                    "gnomad_genomes_homozygous",
                    "thousand_genomes_homozygous",
                    "ensembl_effect",
                ]
            ),
            # for join with clinvar, dbsnp
            models.Index(fields=["release", "chromosome", "position", "reference", "alternative"]),
            # for join with annotation
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                    "ensembl_gene_id",
                ]
            ),
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "position",
                    "reference",
                    "alternative",
                    "refseq_gene_id",
                ]
            ),
            # for join with hgnc
            models.Index(fields=["ensembl_gene_id"]),
            models.Index(fields=["refseq_gene_id"]),
            # for join with case
            models.Index(fields=["case_id"]),
        ]


class Case(models.Model):
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    name = models.CharField(max_length=512)
    index = models.CharField(max_length=32)
    pedigree = JSONField()
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name
