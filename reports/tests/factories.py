import factory

from variants.tests.factories import ProjectFactory
from ..models import ReportTemplate


class ReportTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReportTemplate

    project = factory.SubFactory(ProjectFactory)
    title = factory.Sequence(lambda n: "Template No. %d" % n)
    filename = factory.Sequence(lambda n: "template-%d.docx" % n)
    filesize = 0
    # SHA256 sum of empty file.
    filehash = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
