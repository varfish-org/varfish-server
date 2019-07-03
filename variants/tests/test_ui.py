"""UI tests for the projectroles app"""

import os
import socket
import json
import time
from unittest import skipIf

import binning
from django.contrib import auth
from django.test import LiveServerTestCase
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from projectroles.models import Role, SODAR_CONSTANTS, Project
from projectroles.tests.test_models import ProjectMixin, RoleAssignmentMixin

from variants.tests.factories import SmallVariantSetFactory
from ..models import CaseVariantStats, SampleVariantStatistics, SmallVariant
from clinvar.models import Clinvar

from ._fixtures import CLINVAR_DEFAULTS


# SODAR constants
PROJECT_ROLE_OWNER = SODAR_CONSTANTS["PROJECT_ROLE_OWNER"]
PROJECT_ROLE_DELEGATE = SODAR_CONSTANTS["PROJECT_ROLE_DELEGATE"]
PROJECT_ROLE_CONTRIBUTOR = SODAR_CONSTANTS["PROJECT_ROLE_CONTRIBUTOR"]
PROJECT_ROLE_GUEST = SODAR_CONSTANTS["PROJECT_ROLE_GUEST"]
PROJECT_TYPE_CATEGORY = SODAR_CONSTANTS["PROJECT_TYPE_CATEGORY"]
PROJECT_TYPE_PROJECT = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]
SITE_MODE_TARGET = SODAR_CONSTANTS["SITE_MODE_TARGET"]
SITE_MODE_SOURCE = SODAR_CONSTANTS["SITE_MODE_SOURCE"]

# Local constants
PROJECT_LINK_IDS = [
    "sodar-pr-link-project-roles",
    "sodar-pr-link-project-update",
    "sodar-pr-link-project-create",
    "sodar-pr-link-project-star",
]


User = auth.get_user_model()


SKIP_SELENIUM = "1" == os.environ.get("SKIP_SELENIUM", "0")
SKIP_SELENIUM_MESSAGE = "Selenium tests disabled"


class wait_for_the_attribute_value(object):
    """https://stackoverflow.com/a/43813210/84349

    Usage:

    self.wait.until(wait_for_the_attribute_value((By.ID, "xxx"), "aria-busy", "false"))

    """

    def __init__(self, locator, attribute, value):
        self.locator = locator
        self.attribute = attribute
        self.value = value

    def __call__(self, driver):
        try:
            element_attribute = ec._find_element(driver, self.locator).get_attribute(self.attribute)
            return element_attribute == self.value
        except StaleElementReferenceException:
            return False


class LiveUserMixin:
    """Mixin for creating users to work with LiveServerTestCase"""

    @classmethod
    def _make_user(cls, user_name, superuser):
        """Make user, superuser if superuser=True"""
        kwargs = {
            "username": user_name,
            "password": "password",
            "email": "{}@example.com".format(user_name),
            "is_active": True,
        }

        if superuser:
            user = User.objects.create_superuser(**kwargs)

        else:
            user = User.objects.create_user(**kwargs)

        user.save()
        return user


class TestUIBase(LiveUserMixin, ProjectMixin, RoleAssignmentMixin, LiveServerTestCase):
    """Base class for UI tests"""

    view = None
    kwargs = None
    fixture_setup = None

    def setUp(self):
        # Init the databases
        self.__class__.fixture_setup()

        socket.setdefaulttimeout(60)  # To get around Selenium hangups
        self.wait_time = 30

        # Init headless Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("no-sandbox")  # For Gitlab-CI compatibility
        # Add logging capabilities to fetch the console log of the browser
        d = DesiredCapabilities.CHROME
        d["loggingPrefs"] = {"browser": "ALL"}
        # Set WebDriver
        self.selenium = webdriver.Chrome(chrome_options=options, desired_capabilities=d)
        self.pending = lambda n=self.wait_time: WebDriverWait(self.selenium, n)

        # Prevent ElementNotVisibleException
        self.selenium.set_window_size(1400, 1000)

        # Init roles
        self.role_owner = Role.objects.get_or_create(name=PROJECT_ROLE_OWNER)[0]

        # Init superuser
        self.superuser = self._make_user("admin", True)

        super().setUp()

    def tearDown(self):
        # Shut down Selenium
        self.selenium.quit()
        super().tearDown()

    def build_selenium_url(self, url):
        """Build absolute URL to work with Selenium"""
        return "{}{}".format(self.live_server_url, url)

    def login_and_redirect(self, user, url):
        """Login with Selenium and wait for redirect to given url"""

        self.selenium.get(self.build_selenium_url("/"))

        ########################
        # Logout (if logged in)
        ########################

        try:
            user_button = self.selenium.find_element_by_id("sodar-navbar-user-dropdown")

            user_button.click()

            # Wait for element to be visible
            self.pending().until(
                ec.presence_of_element_located((By.ID, "sodar-navbar-link-logout"))
            )

            try:
                signout_button = self.selenium.find_element_by_id("sodar-navbar-link-logout")
                signout_button.click()

                # Wait for redirect
                self.pending().until(ec.presence_of_element_located((By.ID, "sodar-form-login")))

            except NoSuchElementException:
                pass

        except NoSuchElementException:
            pass

        ########
        # Login
        ########

        self.selenium.get(self.build_selenium_url(url))

        # Submit user data into form
        field_user = self.selenium.find_element_by_id("sodar-login-username")
        # field_user.send_keys(user.username)
        field_user.send_keys(user.username)

        field_pass = self.selenium.find_element_by_id("sodar-login-password")
        field_pass.send_keys("password")

        self.selenium.find_element_by_xpath('//button[contains(., "Log In")]').click()

        # Wait for redirect
        self.pending().until(ec.presence_of_element_located((By.ID, "sodar-navbar-user-dropdown")))

    def compile_url_and_login(self, kwargs={}):
        patched_kwargs = {**self.kwargs, **kwargs}
        self.login_and_redirect(self.superuser, reverse(self.view, kwargs=patched_kwargs))

    def assert_element_exists(self, kwargs, element_id, exists):
        """
        Assert existence of element on webpage based on logged user.
        :param users: User objects to test (list)
        :param url: URL to test (string)
        :param element_id: ID of element (string)
        :param exists: Whether element should or should not exist (boolean)
        """

        self.compile_url_and_login(kwargs)

        if exists:
            self.assertIsNotNone(self.selenium.find_element_by_id(element_id))
        else:
            with self.assertRaises(NoSuchElementException):
                self.selenium.find_element_by_id(element_id)

    def print_log(self):
        """Print the console log of the browser"""
        print("---")
        for i in self.selenium.get_log("browser"):
            print(i)


#: Information for building a project
PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}

BASIC_VAR = {
    "case_id": None,
    "release": "GRCh37",
    "chromosome": "1",
    "chromosome_no": 1,
    "start": None,
    "end": None,
    "bin": None,
    "reference": "A",
    "alternative": "G",
    "var_type": "snv",
    "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
    "in_clinvar": True,
    # frequencies
    "exac_frequency": 0.001,
    "exac_homozygous": 0,
    "exac_heterozygous": 0,
    "exac_hemizygous": 0,
    "thousand_genomes_frequency": 0.001,
    "thousand_genomes_homozygous": 0,
    "thousand_genomes_heterozygous": 0,
    "thousand_genomes_hemizygous": 0,
    "gnomad_exomes_frequency": 0.001,
    "gnomad_exomes_homozygous": 0,
    "gnomad_exomes_heterozygous": 0,
    "gnomad_exomes_hemizygous": 0,
    "gnomad_genomes_frequency": 0.001,
    "gnomad_genomes_homozygous": 0,
    "gnomad_genomes_heterozygous": 0,
    "gnomad_genomes_hemizygous": 0,
    # RefSeq
    "refseq_gene_id": "1234",
    "refseq_transcript_id": "NR_00001.1",
    "refseq_transcript_coding": False,
    "refseq_hgvs_c": "n.111+2T>C",
    "refseq_hgvs_p": "p.=",
    "refseq_effect": ["missense_variant"],
    # ENSEMBL
    "ensembl_gene_id": "ENSG0001",
    "ensembl_transcript_id": "ENST00001",
    "ensembl_transcript_coding": False,
    "ensembl_hgvs_c": "n.111+2T>C",
    "ensembl_hgvs_p": "p.=",
    "ensembl_effect": ["missense_variant"],
}


def fixture_setup_project_case():
    """Fixture setup for a project with a single case and according variant statistics."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    variant_set = SmallVariantSetFactory(case=case)
    casevariantstats = CaseVariantStats.objects.create(variant_set=variant_set)
    SampleVariantStatistics.objects.create(
        stats=casevariantstats,
        sample_name="A",
        ontarget_transitions=1,
        ontarget_transversions=1,
        ontarget_snvs=1,
        ontarget_indels=1,
        ontarget_mnvs=1,
        ontarget_effect_counts={},
        ontarget_indel_sizes={},
        ontarget_dps={},
        ontarget_dp_quantiles=[0.1, 0.2, 0.3, 0.4, 0.5],
        het_ratio=1.0,
        chrx_het_hom=1.0,
    )

    return case


def fixture_setup_project_cases():
    """Fixture setup for a project with a single case and according variant statistics."""
    project = Project.objects.create(**PROJECT_DICT)
    case1 = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    variant_set1 = SmallVariantSetFactory(case=case1)
    casevariantstats = CaseVariantStats.objects.create(variant_set=variant_set1)
    SampleVariantStatistics.objects.create(
        stats=casevariantstats,
        sample_name="A",
        ontarget_transitions=1,
        ontarget_transversions=1,
        ontarget_snvs=1,
        ontarget_indels=1,
        ontarget_mnvs=1,
        ontarget_effect_counts={},
        ontarget_indel_sizes={},
        ontarget_dps={},
        ontarget_dp_quantiles=[0.1, 0.2, 0.3, 0.4, 0.5],
        het_ratio=1.0,
        chrx_het_hom=1.0,
    )
    case2 = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e4",
        name="B",
        index="B",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "B",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    variant_set2 = SmallVariantSetFactory(case=case2)
    casevariantstats = CaseVariantStats.objects.create(variant_set=variant_set2)
    SampleVariantStatistics.objects.create(
        stats=casevariantstats,
        sample_name="B",
        ontarget_transitions=1,
        ontarget_transversions=1,
        ontarget_snvs=1,
        ontarget_indels=1,
        ontarget_mnvs=1,
        ontarget_effect_counts={},
        ontarget_indel_sizes={},
        ontarget_dps={},
        ontarget_dp_quantiles=[0.1, 0.2, 0.3, 0.4, 0.5],
        het_ratio=1.0,
        chrx_het_hom=1.0,
    )
    return (case1, case2)


class TestVariantsCaseListView(TestUIBase):
    """Tests for variants case list view"""

    view = "variants:case-list"
    kwargs = {"project": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4"}
    fixture_setup = fixture_setup_project_case

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_list_item_exists(self):
        """Test if list with case is rendered."""
        self.assert_element_exists(
            {}, "varfish-bg-table-row-{}".format("9b90556b-041e-47f1-bdc7-4d5a4f8357e3"), True
        )


class TestVariantsCaseDetailView(TestUIBase):
    """Tests for the variants case detail view"""

    view = "variants:case-detail"
    kwargs = {
        "project": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
        "case": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    }
    fixture_setup = fixture_setup_project_case

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_detail_overview_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, "card-varfish-vars-case-details-overview", True)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_detail_pedigree_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, "card-varfish-vars-case-details-pedigree", True)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_detail_qc_plots_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, "card-varfish-vars-case-details-qc-plots", True)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_detail_comments_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, "card-varfish-vars-case-details-small-var-comments", True)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_detail_flags_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, "card-varfish-vars-case-details-small-var-flags", True)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_detail_bg_jobs_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, "card-varfish-vars-case-details-bg-jobs", True)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_case_detail_qc_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, "card-varfish-vars-case-details-qc", True)


def fixture_setup_single_variant():
    """Fixture setup for a single individual with a single variant (based on fixture_setup_project_case)"""
    case = fixture_setup_project_case()

    Clinvar.objects.create(
        **{
            **CLINVAR_DEFAULTS,
            "start": 100,
            "end": 100,
            "bin": binning.assign_bin(99, 100),
            "clinical_significance": "pathogenic",
            "clinical_significance_ordered": ["pathogenic"],
            "pathogenic": 2,
            "review_status": ["practice guideline"],
            "review_status_ordered": ["practice guideline"],
        }
    )

    SmallVariant.objects.create(
        **{
            **BASIC_VAR,
            **{
                "case_id": case.pk,
                "set_id": case.latest_variant_set_id(),
                "start": 100,
                "end": 100,
                "bin": binning.assign_bin(99, 100),
            },
        }
    )


EFFECT_FIELDS = {
    "id_effect_disruptive_inframe_deletion": False,
    "id_effect_disruptive_inframe_insertion": False,
    "id_effect_feature_truncation": False,
    "id_effect_exon_loss_variant": False,
    "id_effect_frameshift_elongation": False,
    "id_effect_frameshift_truncation": False,
    "id_effect_frameshift_variant": False,
    "id_effect_inframe_deletion": False,
    "id_effect_inframe_insertion": False,
    "id_effect_internal_feature_elongation": False,
    "id_effect_missense_variant": False,
    "id_effect_mnv": False,
    "id_effect_start_lost": False,
    "id_effect_stop_gained": False,
    "id_effect_stop_retained_variant": False,
    "id_effect_stop_lost": False,
    "id_effect_synonymous_variant": False,
    "id_effect_direct_tandem_duplication": False,
    "id_effect_downstream_gene_variant": False,
    "id_effect_coding_transcript_intron_variant": False,
    "id_effect_intergenic_variant": False,
    "id_effect_upstream_gene_variant": False,
    "id_effect_three_prime_UTR_exon_variant": False,
    "id_effect_three_prime_UTR_intron_variant": False,
    "id_effect_five_prime_UTR_exon_variant": False,
    "id_effect_five_prime_UTR_intron_variant": False,
    "id_effect_non_coding_transcript_exon_variant": False,
    "id_effect_non_coding_transcript_intron_variant": False,
    "id_effect_splice_acceptor_variant": False,
    "id_effect_splice_donor_variant": False,
    "id_effect_splice_region_variant": False,
    "id_effect_structural_variant": False,
    "id_effect_transcript_ablation": False,
    "id_effect_complex_substitution": False,
}


class TestVariantsCaseFilterView(TestUIBase):
    """Tests for the variants case filter view."""

    view = "variants:case-filter"
    kwargs = {
        "project": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
        "case": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    }
    fixture_setup = fixture_setup_single_variant

    def _disable_effect_groups(self):
        """Helper function to disable all effect checkboxes by activating and deactivating the 'all' checkbox."""
        tab = self.selenium.find_element_by_id("effect-tab")
        checkbox = self.selenium.find_element_by_id("id_effect_group_all")
        cross_checkbox = self.selenium.find_element_by_id("id_effect_synonymous_variant")
        # switch tab and wait until change happened
        tab.click()
        self.pending().until(ec.visibility_of(checkbox))
        # initially checkbox all synonymous_variant are unchecked, test for that
        self.pending().until_not(ec.element_to_be_selected(checkbox))
        self.pending().until_not(ec.element_to_be_selected(cross_checkbox))
        # click all to enable it and wait for changes to take place
        checkbox.click()
        self.pending().until(ec.element_to_be_selected(checkbox))
        self.pending().until(ec.element_to_be_selected(cross_checkbox))
        # click all to disable it and wait for changes to take place
        checkbox.click()
        self.pending().until_not(ec.element_to_be_selected(checkbox))
        self.pending().until_not(ec.element_to_be_selected(cross_checkbox))

    def _check_effect_groups(self, group, effect_fields_patch):
        """Helper function for testing the performance of the effect group checkboxes."""
        # login
        self.compile_url_and_login()
        # switch tab and disable effect groups
        self._disable_effect_groups()
        # patch effect fields
        patched_effect_fields = {**EFFECT_FIELDS, **effect_fields_patch}
        # select checkbox effects, if group is provided
        if group:
            self.selenium.find_element_by_id(group).click()
        # check for ticked checkboxes
        for field, value in patched_effect_fields.items():
            self.assertEqual(self.selenium.find_element_by_id(field).is_selected(), value)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_effects_form_select_none(self):
        """Test if effect group checkbox 'all' disables all effects if activated and deactivated."""
        self._check_effect_groups(None, {})

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_effects_form_select_all(self):
        """Test if effect group checkbox 'all' selects all effect checkboxes."""
        self._check_effect_groups("id_effect_group_all", {effect: True for effect in EFFECT_FIELDS})

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_effects_form_select_nonsynonymous(self):
        """Test if effect group checkbox 'nonsynonymous' selects the correct effect checkboxes."""
        self._check_effect_groups(
            "id_effect_group_nonsynonymous",
            {
                "id_effect_disruptive_inframe_deletion": True,
                "id_effect_disruptive_inframe_insertion": True,
                "id_effect_feature_truncation": True,
                "id_effect_exon_loss_variant": True,
                "id_effect_frameshift_elongation": True,
                "id_effect_frameshift_truncation": True,
                "id_effect_frameshift_variant": True,
                "id_effect_inframe_deletion": True,
                "id_effect_inframe_insertion": True,
                "id_effect_internal_feature_elongation": True,
                "id_effect_missense_variant": True,
                "id_effect_mnv": True,
                "id_effect_start_lost": True,
                "id_effect_stop_gained": True,
                "id_effect_stop_lost": True,
                "id_effect_direct_tandem_duplication": True,
                "id_effect_structural_variant": True,
                "id_effect_transcript_ablation": True,
                "id_effect_complex_substitution": True,
            },
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_effects_form_select_splicing(self):
        """Test if effect group checkbox 'splicing' selects the correct effect checkboxes."""
        self._check_effect_groups(
            "id_effect_group_splicing",
            {
                "id_effect_splice_acceptor_variant": True,
                "id_effect_splice_donor_variant": True,
                "id_effect_splice_region_variant": True,
            },
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_effects_form_select_coding(self):
        """Test if effect group checkbox 'coding' selects the correct effect checkboxes."""
        self._check_effect_groups(
            "id_effect_group_coding",
            {"id_effect_stop_retained_variant": True, "id_effect_synonymous_variant": True},
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_effects_form_select_utr_intronic(self):
        """Test if effect group checkbox 'UTR/intronic' selects the correct effect checkboxes."""
        self._check_effect_groups(
            "id_effect_group_utr_intronic",
            {
                "id_effect_coding_transcript_intron_variant": True,
                "id_effect_three_prime_UTR_exon_variant": True,
                "id_effect_three_prime_UTR_intron_variant": True,
                "id_effect_five_prime_UTR_exon_variant": True,
                "id_effect_five_prime_UTR_intron_variant": True,
            },
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_effects_form_select_noncoding(self):
        """Test if effect group checkbox 'noncoding' selects the correct effect checkboxes."""
        self._check_effect_groups(
            "id_effect_group_noncoding",
            {
                "id_effect_downstream_gene_variant": True,
                "id_effect_intergenic_variant": True,
                "id_effect_upstream_gene_variant": True,
                "id_effect_non_coding_transcript_exon_variant": True,
                "id_effect_non_coding_transcript_intron_variant": True,
            },
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_settings_initial_database(self):
        """Test if the initial form settings correspond to the JSON dump textarea by checking the database setting."""
        # login
        self.compile_url_and_login()
        # obtain initial settings from textarea
        settings = json.loads(
            self.selenium.find_element_by_id("settingsDump").get_attribute("value")
        )
        # check if database_select switch is set as expected to refseq
        self.assertEqual(settings["database_select"], "refseq")
        # check if initial setting is as expected
        self.assertTrue(
            self.selenium.find_element_by_xpath(
                '//input[@name="database_select" and @value="refseq"]'
            ).is_selected()
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_settings_export_database_refseq_to_ensembl(self):
        """Test the settings dump export by selecting 'ensembl' in the database selector form."""
        # login
        self.compile_url_and_login()
        # select ensembl as transcript database (input is overlayed by the label)
        self.selenium.find_element_by_xpath('//label[@for="id_database_select_1"]').click()
        # obtain settings textarea and check if new setting was applied
        settings = json.loads(
            self.selenium.find_element_by_id("settingsDump").get_attribute("value")
        )
        self.assertEqual(settings["database_select"], "ensembl")

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_settings_import_database_refseq_to_ensembl(self):
        """Test the settings dump import by changing JSON field to 'ensembl' in the textarea."""
        # login
        self.compile_url_and_login()
        # switch to settings tab and wait for it to be displayed
        self.selenium.find_element_by_id("more-tab").click()
        tab = self.selenium.find_element_by_id("settings-tab")
        self.pending().until(ec.visibility_of(tab))
        tab.click()
        textarea = self.selenium.find_element_by_id("settingsDump")
        self.pending().until(ec.visibility_of(textarea))
        # obtain initial settings from textarea
        settings_json = json.loads(textarea.get_attribute("value"))
        # change value
        settings_json["database_select"] = "ensembl"
        textarea.clear()
        textarea.send_keys(json.dumps(settings_json))
        self.selenium.find_element_by_id("settingsSet").click()
        # check if setting was applied
        self.assertTrue(
            self.selenium.find_element_by_xpath(
                '//input[@name="database_select" and @value="ensembl"]'
            ).is_selected()
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_display_loading(self):
        """Test if submitting the filter initiates the loading response."""
        # login
        self.compile_url_and_login()
        # find & hit button
        button = self.selenium.find_element_by_id("submitFilter")
        self.assertEqual(button.get_attribute("data-event-type"), "submit")
        button.click()
        self.pending().until(ec.presence_of_element_located((By.ID, "logger")))
        self.assertEqual(button.get_attribute("data-event-type"), "cancel")
        # Wait for background job to finish, otherwise database can't be flushed for next test.
        time.sleep(5)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_display_cancel(self):
        """Test if submitting the filter can be canceled."""
        # login
        self.compile_url_and_login()
        # find & hit button
        button = self.selenium.find_element_by_id("submitFilter")
        self.assertEqual(button.get_attribute("data-event-type"), "submit")
        button.click()
        self.pending().until(ec.presence_of_element_located((By.ID, "logger")))
        self.assertEqual(button.get_attribute("data-event-type"), "cancel")
        button.click()
        time.sleep(5)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_id("logger")
        self.assertEqual(
            self.selenium.find_element_by_id("resultsTable").get_attribute("innerHTML"), ""
        )
        self.assertEqual(button.get_attribute("data-event-type"), "submit")

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_display_results(self):
        """Test if submitting the filter yields the expected results."""
        # login
        self.compile_url_and_login()
        # switch tab
        self.selenium.find_element_by_id("frequency-tab").click()
        exac = self.selenium.find_element_by_xpath("//input[@name='exac_enabled']")
        self.pending().until(ec.visibility_of(exac))
        # disable exac and thousand genomes frequency filter
        exac.click()
        self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_enabled']").click()
        # switch tab
        self.selenium.find_element_by_id("quality-tab").click()
        dropdown = self.selenium.find_element_by_id("id_A_fail")
        self.pending().until(ec.visibility_of(dropdown))
        # disable quality filters
        dropdown.click()
        option = self.selenium.find_element_by_xpath("//option[@value='ignore']")
        self.pending().until(ec.visibility_of(option))
        option.click()
        # hit submit button
        self.selenium.find_element_by_id("submitFilter").click()
        # wait for redirect
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "variant-row")))

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_bookmark(self):
        """Test if submitting the filter yields the expected results."""
        # login
        self.compile_url_and_login()
        # switch tab
        self.selenium.find_element_by_id("frequency-tab").click()
        exac = self.selenium.find_element_by_xpath("//input[@name='exac_enabled']")
        self.pending().until(ec.visibility_of(exac))
        # disable exac and thousand genomes frequency filter
        exac.click()
        self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_enabled']").click()
        # switch tab
        self.selenium.find_element_by_id("quality-tab").click()
        dropdown = self.selenium.find_element_by_id("id_A_fail")
        self.pending().until(ec.visibility_of(dropdown))
        # disable quality filters
        dropdown.click()
        option = self.selenium.find_element_by_xpath("//option[@value='ignore']")
        self.pending().until(ec.visibility_of(option))
        option.click()
        # hit submit button
        self.selenium.find_element_by_id("submitFilter").click()
        # wait for redirect
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "variant-row")))
        # bookmark variant (there is only one variant)
        self.selenium.find_element_by_class_name("variant-bookmark").click()
        # save bookmark
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "save")))
        self.selenium.find_element_by_class_name("save").click()
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "fa-bookmark")))

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_training_mode(self):
        """Test if submitting the filter yields the expected results."""
        # login
        self.compile_url_and_login()
        # switch tab
        self.selenium.find_element_by_id("frequency-tab").click()
        exac = self.selenium.find_element_by_xpath("//input[@name='exac_enabled']")
        self.pending().until(ec.visibility_of(exac))
        # disable exac and thousand genomes frequency filter
        exac.click()
        self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_enabled']").click()
        # switch tab
        self.selenium.find_element_by_id("quality-tab").click()
        dropdown = self.selenium.find_element_by_id("id_A_fail")
        self.pending().until(ec.visibility_of(dropdown))
        # disable quality filters
        dropdown.click()
        option = self.selenium.find_element_by_xpath("//option[@value='ignore']")
        self.pending().until(ec.visibility_of(option))
        option.click()
        # hit submit button
        self.selenium.find_element_by_id("submitFilter").click()
        # wait for redirect
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "variant-row")))
        self.selenium.find_element_by_class_name("variant-bookmark").click()
        # save bookmark
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "save")))
        self.selenium.find_element_by_class_name("save").click()
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "fa-bookmark")))
        # switch tab
        self.selenium.find_element_by_id("more-tab").click()
        tab = self.selenium.find_element_by_id("misc-tab")
        self.pending().until(ec.visibility_of(tab))
        tab.click()
        # enable training mode
        training = self.selenium.find_element_by_id("id_training_mode")
        self.pending().until(ec.visibility_of(training))
        training.click()
        # hit submit button
        self.selenium.find_element_by_id("submitFilter").click()
        # wait for redirect
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "variant-row")))
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_class_name("bookmark")

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_filter_case_download(self):
        """Test if submitting the download filter is kicked off."""
        # login
        self.compile_url_and_login()
        # switch tab
        self.selenium.find_element_by_id("frequency-tab").click()
        exac = self.selenium.find_element_by_xpath("//input[@name='exac_enabled']")
        self.pending().until(ec.visibility_of(exac))
        # disable exac and thousand genomes frequency filter
        exac.click()
        self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_enabled']").click()
        # switch tab
        self.selenium.find_element_by_id("quality-tab").click()
        dropdown = self.selenium.find_element_by_id("id_A_fail")
        self.pending().until(ec.visibility_of(dropdown))
        # disable quality filters
        dropdown.click()
        option = self.selenium.find_element_by_xpath("//option[@value='ignore']")
        self.pending().until(ec.visibility_of(option))
        option.click()
        # find and hit download button
        self.selenium.find_element_by_id("submit-menu").click()
        download = self.selenium.find_element_by_xpath(
            '//button[@name="submit" and @value="download"]'
        )
        self.pending().until(ec.visibility_of(download))
        download.click()
        # wait for redirect and refresh page for elements to show up
        self.pending().until(
            ec.presence_of_element_located(
                (By.XPATH, '//h2[contains(text(), "{}")]'.format("Background File Creation Job"))
            )
        )
        time.sleep(5)
        self.selenium.refresh()
        self.pending().until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(text(), "{}")]'.format("Exporting single case to file started"),
                )
            )
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_preset_medgen_relaxed_on_quality_settings(self):
        """Test medgen relaxed preset on a quality setting"""
        # login
        self.compile_url_and_login()
        # select medgen relaxed preset
        self.selenium.find_element_by_id("presets-menu-button").click()
        self.selenium.find_element_by_xpath("//a[@data-preset-name='medgen-relaxed']").click()
        # verify correctness
        self.assertEquals(
            self.selenium.find_element_by_id("id_A_dp_het").get_attribute("value"), "8"
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_preset_medgen_clinvar_on_quality_settings(self):
        """Test medgen clinvar preset on a quality setting"""
        # login
        self.compile_url_and_login()
        # select medgen clinvar preset
        self.selenium.find_element_by_id("presets-menu-button").click()
        self.selenium.find_element_by_xpath("//a[@data-preset-name='medgen-clinvar']").click()
        # verify correctness
        self.assertEqual(
            self.selenium.find_element_by_id("id_A_fail").get_attribute("value"), "ignore"
        )

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_preset_full_exome_on_effect_settings(self):
        """Test full exome preset on the all effect setting"""
        # login
        self.compile_url_and_login()
        # select full exome preset
        self.selenium.find_element_by_id("presets-menu-button").click()
        self.selenium.find_element_by_xpath("//a[@data-preset-name='full-exome']").click()
        # verify correctness
        self.assertTrue(self.selenium.find_element_by_id("id_effect_group_all").is_selected())

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_invalid_form_input_error_rendering(self):
        """Test if invalid form input triggers visual error response rendering."""
        self.compile_url_and_login()
        button = self.selenium.find_element_by_id("submitFilter")
        # create wrong setting
        tab = self.selenium.find_element_by_id("frequency-tab")
        tab.click()
        field = self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_frequency']")
        self.pending().until(ec.visibility_of(field))
        field.clear()
        field.send_keys("10")
        # submit
        button.click()
        time.sleep(5)
        # check for correct error rendering
        self.assertIn("border-danger", tab.get_attribute("class").split())
        self.assertIn("border-danger", field.get_attribute("class").split())

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_corrected_invalid_form_input_error_rendering(self):
        """Test if visual error response rendering is removed when correcting invalid input."""
        self.compile_url_and_login()
        button = self.selenium.find_element_by_id("submitFilter")
        # create wrong setting
        tab = self.selenium.find_element_by_id("frequency-tab")
        tab.click()
        field = self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_frequency']")
        self.pending().until(ec.visibility_of(field))
        field.clear()
        field.send_keys("10")
        # submit
        button.click()
        time.sleep(5)
        # correct invalid input
        field.clear()
        field.send_keys("0.1")
        button.click()
        time.sleep(5)
        self.assertNotIn("border-danger", tab.get_attribute("class").split())
        self.assertNotIn("border-danger", field.get_attribute("class").split())


def fixture_setup_two_variants():
    """Fixture setup for a single individual with a single variant (based on fixture_setup_project_case)"""
    case1, case2 = fixture_setup_project_cases()
    SmallVariant.objects.create(
        **{
            **BASIC_VAR,
            **{
                "case_id": case1.pk,
                "set_id": case1.latest_variant_set_id(),
                "start": 100,
                "end": 100,
                "bin": binning.assign_bin(99, 100),
            },
        }
    )
    SmallVariant.objects.create(
        **{
            **BASIC_VAR,
            **{
                "case_id": case2.pk,
                "set_id": case2.latest_variant_set_id(),
                "start": 200,
                "end": 200,
                "bin": binning.assign_bin(199, 200),
            },
        }
    )


class TestVariantsProjectCasesFilterView(TestUIBase):
    """Tests for the variants joint filter view."""

    view = "variants:project-cases-filter"
    kwargs = {"project": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4"}
    fixture_setup = fixture_setup_two_variants

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_joint_filter_display_loading(self):
        """Test if submitting the filter initiates the loading response."""
        # login
        self.compile_url_and_login()
        # find & hit button
        button = self.selenium.find_element_by_id("submitFilter")
        self.assertEqual(button.get_attribute("data-event-type"), "submit")
        button.click()
        self.pending().until(ec.presence_of_element_located((By.ID, "logger")))
        self.assertEqual(button.get_attribute("data-event-type"), "cancel")
        # Wait for background job to finish, otherwise database can't be flushed for next test.
        time.sleep(5)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_joint_filter_display_cancel(self):
        """Test if submitting the filter can be canceled."""
        # login
        self.compile_url_and_login()
        # find & hit button
        button = self.selenium.find_element_by_id("submitFilter")
        self.assertEqual(button.get_attribute("data-event-type"), "submit")
        button.click()
        self.pending().until(ec.presence_of_element_located((By.ID, "logger")))
        self.assertEqual(button.get_attribute("data-event-type"), "cancel")
        button.click()
        time.sleep(5)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_id("logger")
        self.assertEqual(
            self.selenium.find_element_by_id("resultsTable").get_attribute("innerHTML"), ""
        )
        self.assertEqual(button.get_attribute("data-event-type"), "submit")

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_join_filter_display_results(self):
        """Test if submitting the filter yields the expected results."""
        # login
        self.compile_url_and_login()
        # switch tab
        self.selenium.find_element_by_id("frequency-tab").click()
        exac = self.selenium.find_element_by_xpath("//input[@name='exac_enabled']")
        self.pending().until(ec.visibility_of(exac))
        # disable exac and thousand genomes frequency filter
        exac.click()
        self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_enabled']").click()
        # switch tab
        self.selenium.find_element_by_id("quality-tab").click()
        dropdown = self.selenium.find_element_by_id("id_A_fail")
        self.pending().until(ec.visibility_of(dropdown))
        # disable quality filters
        dropdown.click()
        option = self.selenium.find_element_by_xpath("//option[@value='ignore']")
        self.pending().until(ec.visibility_of(option))
        option.click()
        # hit submit button
        self.selenium.find_element_by_id("submitFilter").click()
        # wait for redirect
        self.pending().until(ec.presence_of_element_located((By.CLASS_NAME, "variant-row")))

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_joint_filter_download(self):
        """Test if submitting the download filter is kicked off."""
        # login
        self.compile_url_and_login()
        # switch tab
        self.selenium.find_element_by_id("frequency-tab").click()
        exac = self.selenium.find_element_by_xpath("//input[@name='exac_enabled']")
        self.pending().until(ec.visibility_of(exac))
        # disable exac and thousand genomes frequency filter
        exac.click()
        self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_enabled']").click()
        # switch tab
        self.selenium.find_element_by_id("quality-tab").click()
        dropdown = self.selenium.find_element_by_id("id_A_fail")
        self.pending().until(ec.visibility_of(dropdown))
        # disable quality filters
        dropdown.click()
        option = self.selenium.find_element_by_xpath("//option[@value='ignore']")
        self.pending().until(ec.visibility_of(option))
        option.click()
        # find and hit download button
        self.selenium.find_element_by_id("submit-menu").click()
        download = self.selenium.find_element_by_xpath(
            '//button[@name="submit" and @value="download"]'
        )
        self.pending().until(ec.visibility_of(download))
        download.click()
        # wait for redirect and refresh page for elements to show up
        self.pending().until(
            ec.presence_of_element_located(
                (By.XPATH, '//h2[contains(text(), "{}")]'.format("Background File Creation Job"))
            )
        )
        time.sleep(5)
        self.selenium.refresh()
        self.pending().until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(text(), "{}")]'.format("Exporting all project cases to file"),
                )
            )
        )


class TestVariantsCaseClinvarView(TestUIBase):
    """Tests for the variants case filter view."""

    view = "variants:case-clinvar"
    kwargs = {
        "project": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
        "case": "9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
    }
    fixture_setup = fixture_setup_single_variant

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_clinvar_display_loading(self):
        """Test if submitting the filter initiates the loading response."""
        # login
        self.compile_url_and_login()
        # find & hit button
        button = self.selenium.find_element_by_id("submitFilter")
        self.assertEqual(button.get_attribute("data-event-type"), "submit")
        button.click()
        self.pending().until(ec.presence_of_element_located((By.ID, "logger")))
        self.assertEqual(button.get_attribute("data-event-type"), "cancel")
        # Wait for background job to finish, otherwise database can't be flushed for next test.
        time.sleep(5)

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_clinvar_display_cancel(self):
        """Test if submitting the filter can be canceled."""
        # login
        self.compile_url_and_login()
        # find & hit button
        button = self.selenium.find_element_by_id("submitFilter")
        self.assertEqual(button.get_attribute("data-event-type"), "submit")
        button.click()
        self.pending().until(ec.presence_of_element_located((By.ID, "logger")))
        self.assertEqual(button.get_attribute("data-event-type"), "cancel")
        button.click()
        time.sleep(5)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_id("logger")
        self.assertEqual(
            self.selenium.find_element_by_id("resultsTable").get_attribute("innerHTML"), ""
        )
        self.assertEqual(button.get_attribute("data-event-type"), "submit")

    @skipIf(SKIP_SELENIUM, SKIP_SELENIUM_MESSAGE)
    def test_variant_clinvar_display_results(self):
        """Test if submitting the filter yields the expected results."""
        # login
        self.compile_url_and_login()
        # hit submit button
        self.selenium.find_element_by_id("submitFilter").click()
        # wait for redirect
        self.pending().until(ec.presence_of_element_located((By.ID, "clinvar-entry-1")))
