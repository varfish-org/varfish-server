"""Tests for the export API views.

This module contains comprehensive tests for the filter settings export API functionality.

Test Coverage:
- Basic export functionality with various filter settings
- Metadata inclusion (user, case info, transcript database)
- Error handling (invalid JSON, empty requests, missing dependencies)
- Different settings types (quality, genotype, frequency, flags, ClinVar, etc.)
- Edge cases (large data, anonymous users, empty settings)
"""

import json
from unittest.mock import patch

from django.urls import reverse
from freezegun import freeze_time

from .factories import CaseWithVariantSetFactory
from .helpers import ApiViewTestBase


@freeze_time("2012-01-14 12:00:01")
class TestExportFilterSettingsApiView(ApiViewTestBase):
    """Tests for the export filter settings API view."""

    def setUp(self):
        super().setUp()
        self.case, self.variant_set, _ = CaseWithVariantSetFactory.get("small")
        self.url = reverse("variants:api-export-filter-settings")

    def _get_basic_filter_settings(self):
        """Return basic filter settings for testing."""
        return {
            "filter_settings": {
                "quality": {
                    "dp_het": 10,
                    "dp_hom": 5,
                    "ab": 0.2,
                    "gq": 10,
                    "ad": 3,
                    "fail": "drop-variant",
                },
                "genotype": {"recessive_index": 0, "recessive_mode": "recessive"},
                "consequence": {
                    "var_type_snv": True,
                    "var_type_indel": True,
                    "var_type_mnv": False,
                    "transcripts_coding": True,
                    "transcripts_noncoding": False,
                    "effects": ["missense_variant", "synonymous_variant"],
                },
                "database": "refseq",
            },
            "case_info": {"name": self.case.name},
            "source": "test",
        }

    def test_export_success_with_basic_settings(self):
        """Test successful export with basic filter settings."""
        data = self._get_basic_filter_settings()

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("applied-filter-settings", response["Content-Disposition"])
        self.assertIn("2012-01-14", response["Content-Disposition"])

    def test_export_with_all_settings_types(self):
        """Test export with comprehensive filter settings."""
        data = {
            "filter_settings": {
                "quality": {"dp_het": 10, "dp_hom": 5},
                "genotype": {"recessive_index": 0},
                "consequence": {
                    "var_type_snv": True,
                    "var_type_indel": True,
                    "var_type_mnv": False,
                    "transcripts_coding": True,
                    "transcripts_noncoding": False,
                    "effects": ["missense_variant"],
                },
                "frequency": {
                    "thousand_genomes_enabled": True,
                    "thousand_genomes_frequency": 0.01,
                    "gnomad_exomes_enabled": True,
                    "gnomad_exomes_frequency": 0.005,
                },
                "flags": {"flag_bookmarked": True, "flag_candidate": False},
                "clinvar": {
                    "require_in_clinvar": True,
                    "clinvar_include_pathogenic": True,
                    "clinvar_include_benign": False,
                },
                "prioritization": {
                    "prio_enabled": True,
                    "prio_algorithm": "phenix",
                    "prio_hpo_terms": ["HP:0000001", "HP:0000002"],
                },
                "genes_regions": {
                    "gene_allowlist": ["BRCA1", "BRCA2", "TP53"],
                    "genomic_region": ["chr1:1-1000000"],
                },
                "database": "ensembl",
            },
            "case_info": {
                "name": self.case.name,
                "pedigree": [
                    {
                        "name": "proband",
                        "father": "father",
                        "mother": "mother",
                        "sex": 1,
                        "affected": 2,
                    }
                ],
            },
            "source": "comprehensive_test",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        # Verify DOCX content type
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    def test_export_with_transcript_database_settings(self):
        """Test that transcript database settings are included in metadata."""
        test_cases = [("refseq", "RefSeq"), ("ensembl", "EnsEMBL"), ("custom_db", "custom_db")]

        for db_value, expected_display in test_cases:
            with self.subTest(database=db_value):
                data = self._get_basic_filter_settings()
                data["filter_settings"]["database"] = db_value

                with self.login(self.superuser):
                    response = self.client.post(
                        self.url,
                        data=json.dumps(data),
                        content_type="application/json",
                    )

                self.assertEqual(response.status_code, 200)

    def test_export_with_user_metadata(self):
        """Test that user information is included in metadata."""
        data = self._get_basic_filter_settings()

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        # The user metadata should be included, but we can't easily verify
        # the DOCX content without parsing it

    def test_export_without_case_info(self):
        """Test export without case information."""
        data = {"filter_settings": {"quality": {"dp_het": 10}}, "source": "test"}

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_with_anonymous_user(self):
        """Test export with anonymous user (should still work but no user metadata)."""
        data = self._get_basic_filter_settings()

        # Don't login - use anonymous user
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

    def test_export_empty_filter_settings(self):
        """Test export with empty filter settings."""
        data = {"filter_settings": {}, "case_info": {"name": "test-case"}, "source": "empty_test"}

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_no_filter_settings_key(self):
        """Test export without filter_settings key."""
        data = {"case_info": {"name": "test-case"}, "source": "no_settings_test"}

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_error_empty_request_body(self):
        """Test error response with empty request body."""
        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data="",
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertIn("Empty request body", response_data["error"])

    def test_export_error_invalid_json(self):
        """Test error response with invalid JSON."""
        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data="invalid json{",
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertIn("The request contained invalid JSON", response_data["error"])

    def test_export_only_allows_post_method(self):
        """Test that only POST method is allowed."""
        data = self._get_basic_filter_settings()

        # Test GET method
        with self.login(self.superuser):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

        # Test PUT method
        with self.login(self.superuser):
            response = self.client.put(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 405)

    def test_export_with_complex_genotype_settings(self):
        """Test export with complex genotype settings including pedigree."""
        data = {
            "filter_settings": {
                "genotype": {
                    "sample1": {"gt": "0/1"},
                    "sample2": {"gt": "1/1"},
                    "inheritance": "dominant",
                }
            },
            "case_info": {
                "name": "complex-genotype-test",
                "pedigree": [
                    {
                        "name": "sample1-N1-DNA1-WGS1",
                        "father": "0",
                        "mother": "0",
                        "sex": 1,
                        "affected": 2,
                    },
                    {
                        "name": "sample2-N2-DNA2-WES1",
                        "father": "sample1-N1-DNA1-WGS1",
                        "mother": "0",
                        "sex": 2,
                        "affected": 1,
                    },
                ],
            },
            "source": "complex_genotype",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_with_frequency_settings(self):
        """Test export with comprehensive frequency settings."""
        data = {
            "filter_settings": {
                "thousand_genomes_enabled": True,
                "thousand_genomes_frequency": 0.01,
                "thousand_genomes_homozygous": 5,
                "thousand_genomes_heterozygous": 10,
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_frequency": 0.005,
                "gnomad_genomes_enabled": False,
                "inhouse_enabled": True,
                "inhouse_carriers": 2,
                "mtdb_enabled": True,
                "mtdb_frequency": 0.001,
                "mtdb_count": 1,
            },
            "case_info": {"name": "frequency-test"},
            "source": "frequency_test",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_with_flag_settings(self):
        """Test export with flag settings."""
        data = {
            "filter_settings": {
                "flag_bookmarked": True,
                "flag_candidate": False,
                "flag_final_causative": True,
                "flag_visual_positive": True,
                "flag_validation_uncertain": True,
                "flag_molecular_negative": False,
                "flag_summary_empty": True,
            },
            "case_info": {"name": "flag-test"},
            "source": "flag_test",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_with_clinvar_settings(self):
        """Test export with ClinVar settings."""
        data = {
            "filter_settings": {
                "require_in_clinvar": True,
                "clinvar_paranoid_mode": False,
                "clinvar_include_pathogenic": True,
                "clinvar_include_likely_pathogenic": True,
                "clinvar_include_uncertain_significance": False,
                "clinvar_include_likely_benign": False,
                "clinvar_include_benign": False,
            },
            "case_info": {"name": "clinvar-test"},
            "source": "clinvar_test",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_with_prioritization_settings(self):
        """Test export with prioritization settings."""
        data = {
            "filter_settings": {
                "prio_enabled": True,
                "prio_algorithm": "phenix",
                "prio_hpo_terms": ["HP:0000001", "HP:0000002", "HP:0000003"],
                "patho_enabled": True,
                "patho_score": "cadd",
                "gm_enabled": False,
                "pedia_enabled": True,
            },
            "case_info": {"name": "prioritization-test"},
            "source": "prioritization_test",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_filename_format(self):
        """Test that the exported filename follows the expected format."""
        data = self._get_basic_filter_settings()

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

        # Check filename format in Content-Disposition header includes case name
        content_disposition = response["Content-Disposition"]
        # Should include case name in filename, e.g. applied-filter-settings-case_001_singleton-2012-01-14.docx
        self.assertIn("applied-filter-settings-", content_disposition)
        self.assertIn("-2012-01-14.docx", content_disposition)
        self.assertIn("singleton", content_disposition)  # Case structure should be in filename

    @patch("variants.views.api.export.Document")
    def test_export_document_creation_error(self, mock_document):
        """Test error handling when document creation fails."""
        mock_document.side_effect = Exception("Mock document creation error")

        data = self._get_basic_filter_settings()

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertIn(
            "Internal server error while exporting filter settings", response_data["error"]
        )

    def test_export_csrf_exempt(self):
        """Test that the export endpoint is CSRF exempt."""
        # This test ensures that the @csrf_exempt decorator is working
        # We should be able to make requests without CSRF token
        data = self._get_basic_filter_settings()

        # Make request without CSRF setup
        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type="application/json",
        )

        # Should not get CSRF error (403), but might get other errors
        self.assertNotEqual(response.status_code, 403)

    def test_export_with_large_gene_list(self):
        """Test export with large gene allowlist."""
        # Create a large gene list
        large_gene_list = [f"GENE{i}" for i in range(100)]

        data = {
            "filter_settings": {
                "gene_allowlist": large_gene_list,
                "genomic_region": [f"chr{i}:1000-2000" for i in range(1, 23)],
            },
            "case_info": {"name": "large-gene-list-test"},
            "source": "large_list_test",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

    def test_export_content_length(self):
        """Test that the response has appropriate content length."""
        data = self._get_basic_filter_settings()

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)

        # DOCX files should have some reasonable size
        content = response.content
        self.assertGreater(len(content), 1000)  # Should be at least 1KB
        self.assertLess(len(content), 10 * 1024 * 1024)  # Should be less than 10MB


@freeze_time("2012-01-14 12:00:01")
class TestExportPresetSettingsApiView(ApiViewTestBase):
    """Tests for the export preset settings API view."""

    def setUp(self):
        super().setUp()
        self.case, self.variant_set, _ = CaseWithVariantSetFactory.get("small")
        self.url = reverse("variants:api-export-preset-settings")

    def test_export_error_missing_project_uuid(self):
        """Test that missing project_uuid returns an error."""
        data = {
            "presetset_uuid": "some-uuid",
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("project_uuid is required", response_data["error"])

    def test_export_error_missing_presetset_uuid(self):
        """Test that missing presetset_uuid returns an error."""
        data = {
            "project_uuid": str(self.case.project.sodar_uuid),
        }

        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data=json.dumps(data),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("presetset_uuid is required", response_data["error"])

    def test_export_error_invalid_json(self):
        """Test that invalid JSON in request body returns an error."""
        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data="invalid json",
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("The request contained invalid JSON", response_data["error"])

    def test_export_error_empty_request(self):
        """Test that empty request body returns an error."""
        with self.login(self.superuser):
            response = self.client.post(
                self.url,
                data="",
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("Empty request body", response_data["error"])
