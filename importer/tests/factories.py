"""Factory classes for models."""
import hashlib

import factory

from variants.tests.factories import CoreCaseFactory

from ..models import (
    CaseImportInfo,
    VariantSetImportInfo,
    CaseVariantType,
    BamQcFile,
    GenotypeFile,
    EffectFile,
    DatabaseInfoFile,
)


class CaseImportInfoFactory(CoreCaseFactory):
    """Factory for the ``CaseImportInfo`` model."""

    class Meta:
        model = CaseImportInfo


class VariantSetImportInfoFactory(factory.django.DjangoModelFactory):
    """Factory for the ``VariantSetImportInfo`` model."""

    case_import_info = factory.SubFactory(CaseImportInfoFactory)
    variant_type = CaseVariantType.SMALL.name

    class Meta:
        model = VariantSetImportInfo


class FileBaseFactory(factory.django.DjangoModelFactory):
    """Base class for file factories."""

    file = factory.django.FileField(filename="dummy.tsv.gz")
    name = factory.Sequence(lambda n: "file-%d.tsv.gz" % n)
    md5 = factory.Sequence(
        lambda n: hashlib.md5(("file-%d.tsv.gz" % n).encode("utf-8")).hexdigest()
    )


class BamQcFileFactory(FileBaseFactory):
    """Factory for the ``BamQcFile`` model."""

    case_import_info = factory.SubFactory(CaseImportInfoFactory)

    class Meta:
        model = BamQcFile


class GenotypeFileFactory(FileBaseFactory):
    """Factory for the ``GenotypeFile`` model."""

    variant_set_import_info = factory.SubFactory(VariantSetImportInfoFactory)

    class Meta:
        model = GenotypeFile


class EffectsFileFactory(FileBaseFactory):
    """Factory for the ``EffectsFile`` model."""

    variant_set_import_info = factory.SubFactory(VariantSetImportInfoFactory)

    class Meta:
        model = EffectFile


class DatabaseInfoFileFactory(FileBaseFactory):
    """Factory for the ``DatabaseInfoFile`` model."""

    variant_set_import_info = factory.SubFactory(VariantSetImportInfoFactory)

    class Meta:
        model = DatabaseInfoFile
