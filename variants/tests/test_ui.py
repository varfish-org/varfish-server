"""UI tests for the projectroles app"""

import socket
from urllib.parse import urlencode

from django.contrib import auth
from django.test import LiveServerTestCase, override_settings
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from projectroles.models import Role, SODAR_CONSTANTS, Project
from projectroles.plugins import get_active_plugins
from projectroles.tests.test_models import ProjectMixin, RoleAssignmentMixin,\
    ProjectInviteMixin, RemoteTargetMixin

from ..models import CaseVariantStats, SampleVariantStatistics, SmallVariant


# SODAR constants
PROJECT_ROLE_OWNER = SODAR_CONSTANTS['PROJECT_ROLE_OWNER']
PROJECT_ROLE_DELEGATE = SODAR_CONSTANTS['PROJECT_ROLE_DELEGATE']
PROJECT_ROLE_CONTRIBUTOR = SODAR_CONSTANTS['PROJECT_ROLE_CONTRIBUTOR']
PROJECT_ROLE_GUEST = SODAR_CONSTANTS['PROJECT_ROLE_GUEST']
PROJECT_TYPE_CATEGORY = SODAR_CONSTANTS['PROJECT_TYPE_CATEGORY']
PROJECT_TYPE_PROJECT = SODAR_CONSTANTS['PROJECT_TYPE_PROJECT']
SITE_MODE_TARGET = SODAR_CONSTANTS['SITE_MODE_TARGET']
SITE_MODE_SOURCE = SODAR_CONSTANTS['SITE_MODE_SOURCE']

# Local constants
PROJECT_LINK_IDS = [
    'sodar-pr-link-project-roles',
    'sodar-pr-link-project-update',
    'sodar-pr-link-project-create',
    'sodar-pr-link-project-star']


User = auth.get_user_model()


class LiveUserMixin:
    """Mixin for creating users to work with LiveServerTestCase"""

    @classmethod
    def _make_user(cls, user_name, superuser):
        """Make user, superuser if superuser=True"""
        kwargs = {
            'username': user_name,
            'password': 'password',
            'email': '{}@example.com'.format(user_name),
            'is_active': True}

        if superuser:
            user = User.objects.create_superuser(**kwargs)

        else:
            user = User.objects.create_user(**kwargs)

        user.save()
        return user


class TestUIBase(
        LiveUserMixin, ProjectMixin, RoleAssignmentMixin, LiveServerTestCase):
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
        options.add_argument('headless')
        options.add_argument('no-sandbox')  # For Gitlab-CI compatibility
        self.selenium = webdriver.Chrome(chrome_options=options)

        # Prevent ElementNotVisibleException
        self.selenium.set_window_size(1400, 1000)

        # Init roles
        self.role_owner = Role.objects.get_or_create(
            name=PROJECT_ROLE_OWNER)[0]

        # Init superuser
        self.superuser = self._make_user('admin', True)

        super().setUp()

    def tearDown(self):
        # Shut down Selenium
        self.selenium.quit()
        super().tearDown()

    def build_selenium_url(self, url):
        """Build absolute URL to work with Selenium"""
        return '{}{}'.format(self.live_server_url, url)

    def login_and_redirect(self, user, url):
        """Login with Selenium and wait for redirect to given url"""

        self.selenium.get(self.build_selenium_url('/'))

        ########################
        # Logout (if logged in)
        ########################

        try:
            user_button = self.selenium.find_element_by_id(
                'sodar-navbar-user-dropdown')

            user_button.click()

            # Wait for element to be visible
            WebDriverWait(self.selenium, self.wait_time).until(
                ec.presence_of_element_located(
                    (By.ID, 'sodar-navbar-link-logout')))

            try:
                signout_button = self.selenium.find_element_by_id(
                    'sodar-navbar-link-logout')
                signout_button.click()

                # Wait for redirect
                WebDriverWait(self.selenium, self.wait_time).until(
                    ec.presence_of_element_located(
                        (By.ID, 'sodar-form-login')))

            except NoSuchElementException:
                pass

        except NoSuchElementException:
            pass

        ########
        # Login
        ########

        self.selenium.get(self.build_selenium_url(url))

        # Submit user data into form
        field_user = self.selenium.find_element_by_id('sodar-login-username')
        # field_user.send_keys(user.username)
        field_user.send_keys(user.username)

        field_pass = self.selenium.find_element_by_id('sodar-login-password')
        field_pass.send_keys('password')

        self.selenium.find_element_by_xpath(
            '//button[contains(., "Log In")]').click()

        # Wait for redirect
        WebDriverWait(self.selenium, self.wait_time).until(
            ec.presence_of_element_located(
                (By.ID, 'sodar-navbar-user-dropdown')))

    def compile_url_and_login(self, kwargs):
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
            self.assertIsNotNone(
                self.selenium.find_element_by_id(element_id))
        else:
            with self.assertRaises(NoSuchElementException):
                self.selenium.find_element_by_id(element_id)


PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}


def fixture_setup_project_case():
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
    casevariantstats = CaseVariantStats.objects.create(
        case=case
    )
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


class TestVariantsCaseListView(TestUIBase):
    """Tests for variants case list view"""

    view = 'variants:case-list'
    kwargs = {'project': '7c599407-6c44-4d9e-81aa-cd8cf3d817a4'}
    fixture_setup = fixture_setup_project_case

    def test_variant_case_list_item_exists(self):
        """Test if list with case is rendered."""
        self.assert_element_exists({}, 'varfish-bg-table-row-{}'.format('9b90556b-041e-47f1-bdc7-4d5a4f8357e3'), True)


class TestVariantsCaseDetailView(TestUIBase):
    """Tests for the variants case detail view"""

    view = 'variants:case-detail'
    kwargs = {
        'project': '7c599407-6c44-4d9e-81aa-cd8cf3d817a4',
        'case': '9b90556b-041e-47f1-bdc7-4d5a4f8357e3',
    }
    fixture_setup = fixture_setup_project_case

    def test_variant_case_detail_overview_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, 'card-varfish-vars-case-details-overview', True)

    def test_variant_case_detail_pedigree_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, 'card-varfish-vars-case-details-pedigree', True)

    def test_variant_case_detail_qc_plots_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, 'card-varfish-vars-case-details-qc-plots', True)

    def test_variant_case_detail_comments_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, 'card-varfish-vars-case-details-comments', True)

    def test_variant_case_detail_flags_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, 'card-varfish-vars-case-details-flags', True)

    def test_variant_case_detail_bg_jobs_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, 'card-varfish-vars-case-details-bg-jobs', True)

    def test_variant_case_detail_qc_card_exists(self):
        """Test if the variant details view gets rendered"""
        self.assert_element_exists({}, 'card-varfish-vars-case-details-qc', True)


def fixture_setup_single_variant():
    case = fixture_setup_project_case()
    basic_var = {
        "case_id": case.pk,
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "var_type": "snv",
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        "in_clinvar": False,
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

    SmallVariant.objects.create(**{**basic_var, **{"position": 100}})


#from django.test import override_settings
#@override_settings(DEBUG=True)
class TestVariantsCaseFilterView(TestUIBase):
    """Tests for the variants case detail view"""

    view = 'variants:case-filter'
    kwargs = {
        'project': '7c599407-6c44-4d9e-81aa-cd8cf3d817a4',
        'case': '9b90556b-041e-47f1-bdc7-4d5a4f8357e3',
    }
    fixture_setup = fixture_setup_single_variant

    def test_variant_filter_case(self):
        """Test"""
        self.compile_url_and_login({})
        self.selenium.find_element_by_xpath("//input[@name='exac_enabled']").click()
        self.selenium.find_element_by_xpath("//input[@name='thousand_genomes_enabled']").click()
        self.selenium.find_element_by_xpath("//option[@value='ignore']").click()
        self.selenium.find_element_by_xpath(
            '//button[@name="submit" and @value="display"]').click()

        # Wait for redirect
        WebDriverWait(self.selenium, self.wait_time).until(
            ec.presence_of_element_located(
                (By.ID, 'variant-details-0')))

    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:clinvar'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:filter-project-cases'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:job-list'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:export-job-detail'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:export-job-resubmit'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:export-job-download'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:distiller-job-detail'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:distiller-job-resubmit'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:project-stats-job-create'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:projects-stats-job-detail'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:export-job-download'
    #     )
    #
    # def test_variant_filter_case(self):
    #     """Test"""
    #     url = reverse(
    #         'variants:export-job-download'
    #     )
