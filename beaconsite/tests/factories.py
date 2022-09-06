from Crypto.PublicKey import RSA
import factory
from projectroles.models import Project

from varfish.users.tests.factories import UserFactory
from variants.tests.factories import CaseFactory, ProjectFactory

from ..models import Consortium, ConsortiumAssignment, ConsortiumMember, Query, Response, Site


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Site

    role = Site.REMOTE
    state = factory.Sequence(lambda n: [Site.ENABLED, Site.DISABLED][n % 2])
    identifier = factory.Sequence(lambda n: "site-%d" % n)
    title = factory.Sequence(lambda n: "Site %d" % n)
    description = factory.Sequence(lambda n: "Description of site %d" % n)
    entrypoint_url = factory.Sequence(lambda n: "http://beacon-%d.example.com/beacon" % n)
    key_algo = Site.RSA_SHA256

    @factory.lazy_attribute
    def private_key(self):
        return RSA.generate(2048).export_key("PEM").decode("ascii")

    @factory.lazy_attribute
    def public_key(self):
        key = RSA.import_key(str(self.private_key).encode("ascii"))
        return key.public_key().export_key("PEM").decode("ascii")


class ConsortiumFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Consortium

    identifier = factory.Sequence(lambda n: "consortium-%d" % n)
    title = factory.Sequence(lambda n: "Consortium %d" % n)
    description = factory.Sequence(lambda n: "Description of consortium %d" % n)


class ConsortiumMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConsortiumMember

    site = factory.SubFactory(SiteFactory)
    consortium = factory.SubFactory(ConsortiumFactory)


class ConsortiumWithLocalAndRemoteSiteFactory(ConsortiumFactory):
    site_local = factory.RelatedFactory(
        ConsortiumMemberFactory,
        factory_related_name="consortium",
        site__role=Site.LOCAL,
        site__state=Site.ENABLED,
    )
    site_remote = factory.RelatedFactory(
        ConsortiumMemberFactory,
        factory_related_name="consortium",
        site__role=Site.REMOTE,
        site__state=Site.ENABLED,
    )


class ConsortiumAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConsortiumAssignment

    consortium = factory.SubFactory(Consortium)
    project = factory.SubFactory(Project)


class QueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Query

    src_site = factory.SubFactory(SiteFactory)
    dst_site = factory.SubFactory(SiteFactory)
    http_url = "/beacon/2"
    http_method = "GET"
    http_header = ""
    http_body = None

    src_case = factory.SubFactory(CaseFactory)
    src_project = factory.LazyAttribute(lambda o: o.src_case.project)
    src_user = factory.SubFactory(UserFactory)

    var_release = "GRCh37"
    var_chrom = "1"
    var_start = factory.Sequence(lambda n: 1_000_000 + n)
    var_end = factory.Sequence(lambda n: 1_000_000 + n)
    var_reference = factory.Sequence(lambda n: "ACGT"[n % 4])
    var_alternative = factory.Sequence(lambda n: "CGTA"[n % 4])


class ResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Response

    query = factory.SubFactory(QueryFactory)

    http_header = ""
    http_body = ""
