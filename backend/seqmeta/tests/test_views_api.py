import datetime
import sys

from django.core import serializers
from django.forms import model_to_dict
from django.urls import reverse
from freezegun import freeze_time

from seqmeta.models import EnrichmentKit, TargetBedFile
from seqmeta.tests.factories import EnrichmentKitFactory, TargetBedFileFactory
from variants.tests.helpers import ApiViewTestBase


def isoformat(s: datetime.datetime) -> str:
    """Helper function that returns an ISO 8601 formatted string without microseconds.

    This is the same as django rest framework returns as string.
    """
    return s.isoformat().replace("+00:00", "Z")


@freeze_time("2012-01-14 12:00:01")
class TestEnrichmentKitApiView(ApiViewTestBase):
    """Tests for ``EnrichmentKit`` API views."""

    def setUp(self):
        super().setUp()
        self.enrichmentkit = EnrichmentKitFactory()

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("seqmeta:api-enrichmentkit-listcreate"))

        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "date_created": isoformat(self.enrichmentkit.date_created),
                "date_modified": isoformat(self.enrichmentkit.date_modified),
                "sodar_uuid": str(self.enrichmentkit.sodar_uuid),
                "identifier": self.enrichmentkit.identifier,
                "title": self.enrichmentkit.title,
                "description": self.enrichmentkit.description,
            }
        ]
        actual = [dict(**x) for x in response.data]
        self.assertEquals(actual, expected)

    def test_create(self):
        post_data = {
            "title": "My Title",
            "identifier": "my-identifier",
        }

        self.assertEqual(EnrichmentKit.objects.count(), 1)
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-enrichmentkit-listcreate",
                ),
                method="POST",
                data=post_data,
                format="json",
            )

        self.assertEqual(response.status_code, 201)
        expected = {
            **post_data,
            "description": None,
            "sodar_uuid": response.data["sodar_uuid"],
            "date_created": response.data["date_created"],
            "date_modified": response.data["date_modified"],
        }
        self.assertDictEqual(response.data, expected)
        self.assertIsNotNone(EnrichmentKit.objects.get(sodar_uuid=response.data["sodar_uuid"]))
        self.assertEqual(EnrichmentKit.objects.count(), 2)

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-enrichmentkit-retrieveupdatedestroy",
                    kwargs={
                        "enrichmentkit": self.enrichmentkit.sodar_uuid,
                    },
                )
            )

        expected = {
            "date_created": isoformat(self.enrichmentkit.date_created),
            "date_modified": isoformat(self.enrichmentkit.date_modified),
            "sodar_uuid": str(self.enrichmentkit.sodar_uuid),
            "identifier": self.enrichmentkit.identifier,
            "title": self.enrichmentkit.title,
            "description": self.enrichmentkit.description,
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected)

    def test_update(self):
        patch_data = {
            "title": "This is a new title",
        }

        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-enrichmentkit-retrieveupdatedestroy",
                    kwargs={
                        "enrichmentkit": self.enrichmentkit.sodar_uuid,
                    },
                ),
                method="PATCH",
                data=patch_data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.enrichmentkit.refresh_from_db()
        self.assertEqual(self.enrichmentkit.title, patch_data["title"])

    def test_destroy(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-enrichmentkit-retrieveupdatedestroy",
                    kwargs={
                        "enrichmentkit": self.enrichmentkit.sodar_uuid,
                    },
                ),
                method="DELETE",
            )

        expected = None
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, expected)

        with self.assertRaises(EnrichmentKit.DoesNotExist):
            EnrichmentKit.objects.get(sodar_uuid=self.enrichmentkit.sodar_uuid)


@freeze_time("2012-01-14 12:00:01")
class TestTargetBedFileApiView(ApiViewTestBase):
    """Tests for ``TargetBedFile`` API views."""

    def setUp(self):
        super().setUp()
        self.targetbedfile = TargetBedFileFactory()
        self.enrichmentkit = self.targetbedfile.enrichmentkit

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqmeta:api-targetbedfile-listcreate",
                    kwargs={"enrichmentkit": self.enrichmentkit.sodar_uuid},
                )
            )

        self.assertEqual(response.status_code, 200)
        expected = [
            {
                "date_created": isoformat(self.targetbedfile.date_created),
                "date_modified": isoformat(self.targetbedfile.date_modified),
                "sodar_uuid": str(self.targetbedfile.sodar_uuid),
                "file_uri": self.targetbedfile.file_uri,
                "genome_release": self.targetbedfile.genome_release,
                "enrichmentkit": self.targetbedfile.enrichmentkit.sodar_uuid,
            }
        ]
        actual = [dict(**x) for x in response.data]
        self.assertEquals(actual, expected)

    def test_create(self):
        post_data = {
            "genome_release": "grch38",
            "file_uri": "s3://varfish-public/some-path.bed.gz",
        }

        self.assertEqual(TargetBedFile.objects.count(), 1)
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-targetbedfile-listcreate",
                    kwargs={"enrichmentkit": self.enrichmentkit.sodar_uuid},
                ),
                method="POST",
                data=post_data,
                format="json",
            )

        self.assertEqual(response.status_code, 201, response.data)
        expected = {
            **post_data,
            "sodar_uuid": response.data["sodar_uuid"],
            "date_created": response.data["date_created"],
            "date_modified": response.data["date_modified"],
            "enrichmentkit": self.targetbedfile.enrichmentkit.sodar_uuid,
        }
        self.assertDictEqual(response.data, expected)
        self.assertIsNotNone(TargetBedFile.objects.get(sodar_uuid=response.data["sodar_uuid"]))
        self.assertEqual(TargetBedFile.objects.count(), 2)

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-targetbedfile-retrieveupdatedestroy",
                    kwargs={
                        "targetbedfile": self.targetbedfile.sodar_uuid,
                    },
                )
            )

        expected = {
            "date_created": isoformat(self.targetbedfile.date_created),
            "date_modified": isoformat(self.targetbedfile.date_modified),
            "sodar_uuid": str(self.targetbedfile.sodar_uuid),
            "enrichmentkit": self.targetbedfile.enrichmentkit.sodar_uuid,
            "file_uri": self.targetbedfile.file_uri,
            "genome_release": self.targetbedfile.genome_release,
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected)

    def test_update(self):
        patch_data = {
            "genome_release": "grch38",
            "file_uri": "s3://varfish-public/some-path.bed.gz",
        }

        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-targetbedfile-retrieveupdatedestroy",
                    kwargs={
                        "targetbedfile": self.targetbedfile.sodar_uuid,
                    },
                ),
                method="PATCH",
                data=patch_data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.targetbedfile.refresh_from_db()
        self.assertEqual(self.targetbedfile.file_uri, patch_data["file_uri"])
        self.assertEqual(self.targetbedfile.genome_release, patch_data["genome_release"])

    def test_destroy(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "seqmeta:api-targetbedfile-retrieveupdatedestroy",
                    kwargs={
                        "targetbedfile": self.targetbedfile.sodar_uuid,
                    },
                ),
                method="DELETE",
            )

        expected = None
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, expected)

        with self.assertRaises(TargetBedFile.DoesNotExist):
            TargetBedFile.objects.get(sodar_uuid=self.targetbedfile.sodar_uuid)
