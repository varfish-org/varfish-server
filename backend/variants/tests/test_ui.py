"""UI tests for the projectroles app"""

import os
import time

from django.contrib import auth
from django.urls import reverse
from projectroles.models import SODAR_CONSTANTS
import projectroles.tests.test_ui
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec

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


class wait_for_the_attribute_endswith_value(object):
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
            return element_attribute.endswith(self.value)
        except StaleElementReferenceException:
            return False


class wait_for_element_endswith_value(object):
    """https://stackoverflow.com/a/43813210/84349

    Usage:

    self.wait.until(wait_for_the_attribute_value((By.ID, "xxx"), "aria-busy", "false"))

    """

    def __init__(self, element, attribute, value):
        self.element = element
        self.attribute = attribute
        self.value = value

    def __call__(self, driver):
        try:
            element_attribute = self.element.get_attribute(self.attribute)
            return element_attribute.endswith(self.value)
        except StaleElementReferenceException:
            return False


class element_has_class_locator(object):
    """An expectation for checking that an element has a particular css class.
       locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, locator, css_class):
        self.locator = locator
        self.css_class = css_class

    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element

        if self.css_class in element.get_attribute("class"):
            return element
        else:
            return False


class element_has_class(object):
    """An expectation for checking that an element has a particular css class.
       locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self, element, css_class):
        self.element = element
        self.css_class = css_class

    def __call__(self, driver):
        if self.css_class in self.element.get_attribute("class"):
            return self.element
        else:
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


class UITestBase(projectroles.tests.test_ui.UITestBase):
    """Base class for UI tests"""

    def compile_url_and_login(self, kwargs={}):
        self.login_and_redirect(self.superuser, reverse(self.view, kwargs=kwargs))

    def _disable_filters(self, case_or_project):
        self.selenium.find_element_by_id("quick-presets-button").click()
        self.selenium.find_element_by_xpath("//a[@data-preset-name='whole-exome']").click()
        time.sleep(1)

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
    # new mehari effects
    "id_effect_coding_sequence_variant": False,
    "id_effect_conservative_inframe_deletion": False,
    "id_effect_conservative_inframe_insertion": False,
    "id_effect_intron_variant": False,
    "id_effect_splice_donor_5th_base_variant": False,
    "id_effect_splice_donor_region_variant": False,
    "id_effect_splice_polypyrimidine_tract_variant": False,
    "id_effect_start_retained_variant": False,
    "id_effect_transcript_amplification": False,
}
