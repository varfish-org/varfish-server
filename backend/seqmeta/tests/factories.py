import factory

from seqmeta.models import EnrichmentKit, TargetBedFile


class EnrichmentKitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EnrichmentKit

    identifier = factory.Sequence(lambda n: f"enrichment-kit-{n}")
    title = factory.Sequence(lambda n: f"Enrichment Kit {n}")


class TargetBedFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TargetBedFile

    enrichmentkit = factory.SubFactory(EnrichmentKitFactory)
    file_uri = factory.Sequence(lambda n: f"s3://some-bucket/some-file-{n}.bed.gz")
    genome_release = TargetBedFile.GRCH37
