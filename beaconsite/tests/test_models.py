"""Test models and factories."""
from django.core.exceptions import ValidationError
from test_plus.test import TestCase

from .factories import (
    SiteFactory,
    ConsortiumFactory,
    ConsortiumMemberFactory,
    ConsortiumWithLocalAndRemoteSiteFactory,
    QueryFactory,
    ResponseFactory,
)
from ..models import Site, Consortium, ConsortiumMember, Query, Response


class TestSite(TestCase):
    def test_create(self):
        self.assertEqual(Site.objects.count(), 0)
        SiteFactory()
        self.assertEqual(Site.objects.count(), 1)

    def test_check_only_one_local_site_update(self):
        SiteFactory(role=Site.LOCAL, state=Site.ENABLED)
        second = SiteFactory(role=Site.REMOTE, state=Site.ENABLED)
        second.role = Site.LOCAL
        with self.assertRaises(ValidationError):
            second.full_clean()

    def test_require_public_key_for_asymmetric_encryption(self):
        pass


class TestConsortium(TestCase):
    def test_create(self):
        self.assertEqual(Consortium.objects.count(), 0)
        ConsortiumFactory()
        self.assertEqual(Consortium.objects.count(), 1)


class TestConsortiumMember(TestCase):
    def test_create(self):
        self.assertEqual(ConsortiumMember.objects.count(), 0)
        ConsortiumMemberFactory()
        self.assertEqual(ConsortiumMember.objects.count(), 1)

    def test_create_with_related(self):
        self.assertEqual(Consortium.objects.count(), 0)
        self.assertEqual(ConsortiumMember.objects.count(), 0)
        ConsortiumWithLocalAndRemoteSiteFactory()
        self.assertEqual(ConsortiumMember.objects.count(), 2)
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Consortium.objects.count(), 1)


class TestQuery(TestCase):
    def test_create(self):
        self.assertEqual(Query.objects.count(), 0)
        QueryFactory()
        self.assertEqual(Query.objects.count(), 1)


class TestRespnose(TestCase):
    def test_create(self):
        self.assertEqual(Query.objects.count(), 0)
        self.assertEqual(Response.objects.count(), 0)
        ResponseFactory()
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(Response.objects.count(), 1)
