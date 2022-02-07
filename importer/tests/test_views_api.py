from varfish import __version__ as varfish_version
from varfish.api_utils import VARFISH_API_DEFAULT_VERSION, VARFISH_API_MEDIA_TYPE

import os
from itertools import chain

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.forms import model_to_dict

from variants.tests.helpers import (
    ApiViewTestBase,
    VARFISH_INVALID_VERSION,
    VARFISH_INVALID_MIMETYPE,
)
from variants.tests.test_views_api import transmogrify_pedigree

from ..models import CaseImportInfo, VariantSetImportInfo, CaseVariantType, BamQcFile, GenotypeFile
from .factories import (
    CaseImportInfoFactory,
    VariantSetImportInfoFactory,
    BamQcFileFactory,
    GenotypeFileFactory,
)

#: A known invalid MIME type.
INVALID_MIMETYPE = "application/vnd.bihealth.invalid+json"
#: A known invalid version.
INVALID_VERSION = "0.0.0"
#: The known valid MIME type.
VALID_MIMETYPE = "application/vnd.bihealth.varfish+json"
#: A known valid version.
VALID_VERSION = varfish_version

#: The User model to use.
User = get_user_model()

# TODO: add tests that include permission testing


def helper_model_to_dict(obj, related, related_key, exclude):
    exclude = list(chain(("id", "project", "status"), exclude or ()))
    result = model_to_dict(obj, exclude=exclude)
    # Any of the follow could have been excluded.
    result[related_key] = related.sodar_uuid
    if "sodar_uuid" in result:
        result["sodar_uuid"] = str(result["sodar_uuid"])
    return result


def case_import_info_to_dict(case_import_info, project, exclude=None):
    result = helper_model_to_dict(case_import_info, project, "project", exclude)
    if result.get("owner"):
        result["owner"] = User.objects.get(id=int(result["owner"])).username
    if "pedigree" in result:
        result["pedigree"] = transmogrify_pedigree(result["pedigree"])
    for key in ("bam_qc_files", "variant_sets"):
        result[key] = []
    return result


class TestCaseImportInfoApiViews(ApiViewTestBase):
    """Tests for CaseImportInfo API views."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case_import_info = CaseImportInfoFactory(owner=self.user)
        self.project = self.case_import_info.project

    def test_list(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "importer:api-case-import-info-list-create",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = [
                {
                    **case_import_info_to_dict(
                        self.case_import_info, self.project, exclude=("case",)
                    ),
                }
            ]
            response_content = []
            for entry in response.data:  # remove some warts
                entry = dict(entry)
                entry.pop("date_created")  # complex; not worth testing
                entry.pop("date_modified")  # the same
                response_content.append(entry)
            self.assertEquals(response_content, expected)

    def test_create(self):
        obj = CaseImportInfoFactory(project=self.project)
        obj.pedigree = transmogrify_pedigree(obj.pedigree)
        obj.delete()
        post_data = case_import_info_to_dict(obj, self.project, exclude=("sodar_uuid",))

        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-case-import-info-list-create",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                method="POST",
                data=post_data,
                format="json",
            )

            expected = post_data
            expected.pop("case")
            expected["owner"] = self.user.username
            self.assertEqual(response.status_code, 201)
            obj_uuid = response.data.pop("sodar_uuid")
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEquals(response.data, expected)
            self.assertIsNotNone(CaseImportInfo.objects.get(sodar_uuid=obj_uuid))

    def test_retrieve(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-case-import-info-retrieve-update-destroy",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                    },
                )
            )

            expected = {
                **case_import_info_to_dict(self.case_import_info, self.project, exclude=("case",)),
                "bam_qc_files": [],
                "variant_sets": [],
            }
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.status_code, 200)
            self.maxDiff = None
            self.assertEqual(response.data, expected)

    def test_update(self):
        obj_data = case_import_info_to_dict(
            self.case_import_info, self.project, exclude=("pedigree",)
        )
        obj_data["pedigree"] = transmogrify_pedigree(self.case_import_info.pedigree)

        post_data = {
            "name": "UPDATED name",
            "notes": "UPDATED notes",
        }

        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-case-import-info-retrieve-update-destroy",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                    },
                ),
                method="PATCH",
                data=post_data,
                format="json",
            )

            self.assertEqual(response.status_code, 200)
            expected = {
                **obj_data,
                **post_data,
            }
            expected.pop("case")
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.data, expected)

            case = CaseImportInfo.objects.get(sodar_uuid=self.case_import_info.sodar_uuid)
            self.assertEqual(case.name, post_data["name"])
            self.assertEqual(case.notes, post_data["notes"])

    def test_destroy(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-case-import-info-retrieve-update-destroy",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                    },
                ),
                method="DELETE",
            )

            expected = None
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.data, expected)

            with self.assertRaises(CaseImportInfo.DoesNotExist):
                CaseImportInfo.objects.get(sodar_uuid=self.case_import_info.sodar_uuid)


def variant_set_import_info_to_dict(variant_set_import_info, case_import_info, exclude=None):
    result = helper_model_to_dict(
        variant_set_import_info, case_import_info, "case_import_info", exclude
    )
    for key in ("genotype_files", "effect_files", "db_info_files"):
        result[key] = []
    return result


class TestVariantSetImportInfoApiViews(ApiViewTestBase):
    """Tests for VariantSetImportInfo API views."""

    def setUp(self):
        super().setUp()
        self.variant_set_import_info = VariantSetImportInfoFactory()
        self.case_import_info = self.variant_set_import_info.case_import_info
        self.project = self.case_import_info.project

    def test_list(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-variant-set-import-info-list-create",
                    kwargs={"caseimportinfo": self.case_import_info.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = [
                {
                    **variant_set_import_info_to_dict(
                        self.variant_set_import_info, self.case_import_info
                    ),
                    "genotype_files": [],
                    "effect_files": [],
                    "db_info_files": [],
                }
            ]
            response_content = []
            for entry in response.data:  # remove some warts
                entry = dict(entry)
                entry.pop("date_created")  # complex; not worth testing
                entry.pop("date_modified")  # the same
                response_content.append(entry)
            self.assertEquals(response_content, expected)

    def test_create(self):
        obj = VariantSetImportInfoFactory(
            case_import_info=self.case_import_info, variant_type=CaseVariantType.STRUCTURAL.name
        )
        obj.delete()
        post_data = variant_set_import_info_to_dict(
            obj, self.case_import_info, exclude=("sodar_uuid",)
        )

        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-variant-set-import-info-list-create",
                    kwargs={"caseimportinfo": self.case_import_info.sodar_uuid},
                ),
                method="POST",
                data=post_data,
                format="json",
            )

            expected = post_data
            self.assertEqual(response.status_code, 201)
            obj_uuid = response.data.pop("sodar_uuid")
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEquals(response.data, expected)
            self.assertIsNotNone(VariantSetImportInfo.objects.get(sodar_uuid=obj_uuid))

    def test_retrieve(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-variant-set-import-info-retrieve-update-destroy",
                    kwargs={
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                        "variantsetimportinfo": self.variant_set_import_info.sodar_uuid,
                    },
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = variant_set_import_info_to_dict(
                self.variant_set_import_info, self.case_import_info
            )
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.data, expected)

    def test_update(self):
        obj_data = variant_set_import_info_to_dict(
            self.variant_set_import_info, self.case_import_info
        )

        post_data = {
            "variant_type": CaseVariantType.STRUCTURAL.name,
        }

        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-variant-set-import-info-retrieve-update-destroy",
                    kwargs={
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                        "variantsetimportinfo": self.variant_set_import_info.sodar_uuid,
                    },
                ),
                method="PATCH",
                data=post_data,
                format="json",
            )

            self.assertEqual(response.status_code, 200)
            expected = {
                **obj_data,
                **post_data,
            }
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.data, expected)

            case_import_info = VariantSetImportInfo.objects.get(
                sodar_uuid=self.variant_set_import_info.sodar_uuid
            )
            self.assertEqual(case_import_info.variant_type, post_data["variant_type"])

    def test_destroy(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-variant-set-import-info-retrieve-update-destroy",
                    kwargs={
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                        "variantsetimportinfo": self.variant_set_import_info.sodar_uuid,
                    },
                ),
                method="DELETE",
            )

            expected = None
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.data, expected)

            with self.assertRaises(VariantSetImportInfo.DoesNotExist):
                VariantSetImportInfo.objects.get(sodar_uuid=self.variant_set_import_info.sodar_uuid)


def bam_qc_file_to_dict(bam_qc_file, case_import_info, exclude=None):
    return helper_model_to_dict(
        bam_qc_file, case_import_info, "case_import_info", chain(exclude or (), ("file",))
    )


class TestBamQcFileApiViews(ApiViewTestBase):
    """Tests for BamQcFile API views."""

    def setUp(self):
        super().setUp()
        self.bam_qc_file = BamQcFileFactory()
        self.case_import_info = self.bam_qc_file.case_import_info

    def test_list(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-bam-qc-file-list-create",
                    kwargs={"caseimportinfo": self.case_import_info.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = [bam_qc_file_to_dict(self.bam_qc_file, self.case_import_info)]
            response_content = []
            for entry in response.data:  # remove some warts
                entry = dict(entry)
                entry.pop("date_created")  # complex; not worth testing
                entry.pop("date_modified")  # the same
                response_content.append(entry)
            self.assertEquals(response_content, expected)

    def test_create(self):
        obj = BamQcFileFactory(case_import_info=self.case_import_info,)
        obj.delete()
        post_data = bam_qc_file_to_dict(obj, self.case_import_info, exclude=("sodar_uuid",))

        with self.login(self.user):
            with open(
                os.path.join(os.path.dirname(__file__), "data", "example.tsv"), "rb"
            ) as upload_file:
                response = self.request_knox(
                    reverse(
                        "importer:api-bam-qc-file-list-create",
                        kwargs={"caseimportinfo": self.case_import_info.sodar_uuid},
                    ),
                    format="multipart",
                    method="POST",
                    data={**post_data, "file": upload_file},
                )

            expected = post_data
            self.assertEqual(response.status_code, 201)
            obj_uuid = response.data.pop("sodar_uuid")
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEquals(response.data, expected)
            self.assertIsNotNone(BamQcFile.objects.get(sodar_uuid=obj_uuid))

    def test_retrieve(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-bam-qc-file-retrieve-destroy",
                    kwargs={
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                        "bamqcfile": self.bam_qc_file.sodar_uuid,
                    },
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = bam_qc_file_to_dict(self.bam_qc_file, self.case_import_info)
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.data, expected)

    def test_destroy(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-bam-qc-file-retrieve-destroy",
                    kwargs={
                        "caseimportinfo": self.case_import_info.sodar_uuid,
                        "bamqcfile": self.bam_qc_file.sodar_uuid,
                    },
                ),
                method="DELETE",
            )

            expected = None
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.data, expected)

            with self.assertRaises(BamQcFile.DoesNotExist):
                BamQcFile.objects.get(sodar_uuid=self.bam_qc_file.sodar_uuid)


def genotype_file_to_dict(genotype_file, variant_set_import_info, exclude=None):
    return helper_model_to_dict(
        genotype_file,
        variant_set_import_info,
        "variant_set_import_info",
        chain(exclude or (), ("file",)),
    )


class TestGenotypeFileApiViews(ApiViewTestBase):
    """Tests for GenotypeFile API views."""

    def setUp(self):
        super().setUp()
        self.genotype_file = GenotypeFileFactory()
        self.variant_set_import_info = self.genotype_file.variant_set_import_info

    def test_list(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-genotype-file-list-create",
                    kwargs={"variantsetimportinfo": self.variant_set_import_info.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = [genotype_file_to_dict(self.genotype_file, self.variant_set_import_info)]
            response_content = []
            for entry in response.data:  # remove some warts
                entry = dict(entry)
                entry.pop("date_created")  # complex; not worth testing
                entry.pop("date_modified")  # the same
                response_content.append(entry)
            self.assertEquals(response_content, expected)

    def test_create(self):
        obj = GenotypeFileFactory(variant_set_import_info=self.variant_set_import_info,)
        obj.delete()
        post_data = genotype_file_to_dict(
            obj, self.variant_set_import_info, exclude=("sodar_uuid",)
        )

        with self.login(self.user):
            with open(
                os.path.join(os.path.dirname(__file__), "data", "example.tsv"), "rb"
            ) as upload_file:
                response = self.request_knox(
                    reverse(
                        "importer:api-genotype-file-list-create",
                        kwargs={"variantsetimportinfo": self.variant_set_import_info.sodar_uuid},
                    ),
                    method="POST",
                    format="multipart",
                    data={**post_data, "file": upload_file},
                )

            expected = post_data
            self.assertEqual(response.status_code, 201)
            obj_uuid = response.data.pop("sodar_uuid")
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEquals(response.data, expected)
            self.assertIsNotNone(GenotypeFile.objects.get(sodar_uuid=obj_uuid))

    def test_retrieve(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-genotype-file-retrieve-destroy",
                    kwargs={
                        "variantsetimportinfo": self.variant_set_import_info.sodar_uuid,
                        "genotypefile": self.genotype_file.sodar_uuid,
                    },
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = genotype_file_to_dict(self.genotype_file, self.variant_set_import_info)
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.data, expected)

    def test_destroy(self):
        with self.login(self.user):
            response = self.request_knox(
                reverse(
                    "importer:api-genotype-file-retrieve-destroy",
                    kwargs={
                        "variantsetimportinfo": self.variant_set_import_info.sodar_uuid,
                        "genotypefile": self.genotype_file.sodar_uuid,
                    },
                ),
                method="DELETE",
            )

            expected = None
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.data, expected)

            with self.assertRaises(GenotypeFile.DoesNotExist):
                GenotypeFile.objects.get(sodar_uuid=self.genotype_file.sodar_uuid)
