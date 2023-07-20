from django.utils import timezone
import factory

from cases.tests.factories import IndividualFactory, PedigreeFactory
from cases_files.models import (
    AbstractFile,
    IndividualExternalFile,
    IndividualInternalFile,
    MimeTypes,
    PedigreeExternalFile,
    PedigreeInternalFile,
)
from cases_import.proto import FileDesignation
from variants.tests.factories import CaseFactory


class AbstractFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(timezone.now)
    date_modified = factory.LazyFunction(timezone.now)

    case = factory.SubFactory(CaseFactory)
    path = factory.Sequence(lambda n: f"file-{n}.bam")

    designation = FileDesignation.READ_ALIGNMENTS.value
    genomebuild = AbstractFile.GENOMEBUILD_GRCH38
    mimetype = MimeTypes.BAM.value


class ExternalFileFactory(AbstractFileFactory):
    class Meta:
        abstract = True

    available = True
    last_checked = factory.LazyFunction(timezone.now)


class IndividualExternalFileFactory(ExternalFileFactory):
    class Meta:
        model = IndividualExternalFile

    individual = factory.SubFactory(IndividualFactory)


class PedigreeExternalFileFactory(ExternalFileFactory):
    class Meta:
        model = PedigreeExternalFile

    pedigree = factory.SubFactory(PedigreeFactory)


class InternalFileFactory(AbstractFileFactory):
    class Meta:
        abstract = True

    checksum = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class IndividualInternalFileFactory(InternalFileFactory):
    class Meta:
        model = IndividualInternalFile

    individual = factory.SubFactory(IndividualFactory)


class PedigreeInternalFileFactory(InternalFileFactory):
    class Meta:
        model = PedigreeInternalFile

    pedigree = factory.SubFactory(PedigreeFactory)
