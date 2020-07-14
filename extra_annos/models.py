import typing

from django.contrib.postgres.fields import JSONField
from django.db import models
from postgres_copy import CopyManager

import attr


class ExtraAnnoField(models.Model):
    """Description of an extra annotation field."""

    #: The index of the field.
    field = models.IntegerField()
    #: The label of the field.
    label = models.CharField(max_length=128)

    #: Allows bulk import
    objects = CopyManager()

    class Meta:
        ordering = ("field",)


class ExtraAnno(models.Model):
    """Extra annotation."""

    class Meta:
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
    #: Annotation data.
    anno_data = JSONField(default={})

    #: Allows bulk import
    objects = CopyManager()


TAugmentedExtraAnno = typing.TypeVar("AugmentedExtraAnno")


@attr.s(frozen=True, auto_attribs=True)
class AugmentedExtraAnno:
    release: str
    chromosome: str
    start: int
    end: int
    bin: int
    reference: str
    alternative: str
    annotations: typing.Dict[str, typing.Any]

    @staticmethod
    def create(extra_anno: ExtraAnno, fields: typing.List[ExtraAnnoField]) -> TAugmentedExtraAnno:
        return AugmentedExtraAnno(
            release=extra_anno.release,
            chromosome=extra_anno.chromosome,
            start=extra_anno.start,
            end=extra_anno.end,
            bin=extra_anno.bin,
            reference=extra_anno.reference,
            alternative=extra_anno.alternative,
            annotations={field.label: value for field, value in zip(fields, extra_anno.anno_data)},
        )
