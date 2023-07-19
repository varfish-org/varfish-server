import datetime

import factory

from cases_files.models import AbstractFile, ExternalFile, InternalFile, MimeTypes
from cases_import.proto import FileDesignation
from variants.tests.factories import CaseFactory


class AbstractFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    case = factory.SubFactory(CaseFactory)

    path = factory.Sequence(lambda n: f"file-{n}.bam")

    designation = FileDesignation.READ_ALIGNMENTS.value
    genomebuild = AbstractFile.GENOMEBUILD_GRCH38
    mimetype = MimeTypes.BAM.value


class ExternalFileFactory(AbstractFileFactory):
    class Meta:
        model = ExternalFile

    available = True
    last_checked = factory.LazyFunction(datetime.datetime.now)


class InternalFileFactory(AbstractFileFactory):
    class Meta:
        model = InternalFile

    checksum = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
