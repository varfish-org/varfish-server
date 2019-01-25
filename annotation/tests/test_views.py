"""Tests for the filter view"""

from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from test_plus.test import TestCase

from projectroles.models import Project
from variants.models import SmallVariant
from frequencies.models import Exac, GnomadGenomes, GnomadExomes, ThousandGenomes

from .. import views
import json
from ..models import Annotation
from geneinfo.models import Mim2geneMedgen


PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}


class TestViewBase(TestCase):
    """Base class for view testing."""

    setup_case_in_db = None

    def setUp(self):
        self.project_id = self.__class__.setup_case_in_db()

        self.request_factory = RequestFactory()

        # setup super user
        self.user = self.make_user("superuser")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()


def fixture_setup_annotation():
    """Setup test case 1 -- a singleton with variants for gene blacklist filter."""
    project = Project.objects.create(**PROJECT_DICT)
    # Basic variant settings.
    basic_var = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": 100,
        "reference": "A",
        "alternative": "G",
        "ac": None,
        "ac_afr": 1,
        "ac_amr": 0,
        "ac_eas": 0,
        "ac_fin": 0,
        "ac_nfe": 0,
        "ac_oth": 0,
        "an": None,
        "an_afr": 8726,
        "an_amr": 838,
        "an_eas": 1620,
        "an_fin": 3464,
        "an_nfe": 14996,
        "an_oth": 982,
        "hemi": None,
        "hemi_afr": None,
        "hemi_amr": None,
        "hemi_eas": None,
        "hemi_fin": None,
        "hemi_nfe": None,
        "hemi_oth": None,
        "hom": 0,
        "hom_afr": 0,
        "hom_amr": 0,
        "hom_eas": 0,
        "hom_fin": 0,
        "hom_nfe": 0,
        "hom_oth": 0,
        "popmax": "AFR",
        "ac_popmax": 1,
        "an_popmax": 8726,
        "af_popmax": 0.0001146,
        "hemi_popmax": None,
        "hom_popmax": 0,
        "af": None,
        "af_afr": 0.0001146,
        "af_amr": 0.0,
        "af_eas": 0.0,
        "af_fin": 0.0,
        "af_nfe": 0.0,
        "af_oth": 0.0,
    }
    Exac.objects.create(
        **{
            **basic_var,
            **{"ac_sas": 0, "an_sas": 323, "hemi_sas": None, "hom_sas": 0, "af_sas": 0.0},
        }
    )
    ThousandGenomes.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        ac=3,
        an=5008,
        het=3,
        hom=0,
        af=0.000058,
        af_afr=0.0,
        af_amr=0.0054,
        af_eas=0.0,
        af_eur=0.0,
        af_sas=0.0,
    )
    GnomadExomes.objects.create(
        **{
            **basic_var,
            **{
                "ac_asj": 0,
                "ac_sas": 0,
                "an_asj": 323,
                "an_sas": 932,
                "hemi_asj": None,
                "hemi_sas": None,
                "hom_asj": 0,
                "hom_sas": 0,
                "af_asj": 0.0,
                "af_sas": 0.0,
            },
        }
    )
    GnomadGenomes.objects.create(
        **{
            **basic_var,
            **{"ac_asj": 0, "an_asj": 323, "hemi_asj": None, "hom_asj": 0, "af_asj": 0.0},
        }
    )

    Annotation.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        database="refseq",
        effect=[],
        gene_id="123",
        transcript_id="123",
        transcript_coding=False,
        hgvs_c=None,
        hgvs_p=None,
    )

    return project.sodar_uuid


class TestVariantView(TestViewBase):
    """Test the variant view."""

    #: Fixture for setup
    setup_case_in_db = fixture_setup_annotation

    def test_render(self):
        """Test rendering the annotation variant view."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "annotation:variant",
                    kwargs={
                        "project": self.project_id,
                        "database": "refseq",
                        "release": "GRCh37",
                        "chromosome": "1",
                        "position": 100,
                        "reference": "A",
                        "alternative": "G",
                    },
                )
            )

        # check for correct response code
        self.assertEqual(response.status_code, 200)
        # check for correct values
        self.assertEqual(response.context["position"], "100")
        self.assertEqual(response.context["gnomadexomes"]["an_sas"], 932)
        self.assertEqual(response.context["exac"]["an_sas"], 323)
        self.assertEqual(response.context["gnomadgenomes"]["an_asj"], 323)
        self.assertEqual(response.context["thousandgenomes"]["af_amr"], 0.0054)
        self.assertEqual(response.context["data"][0]["transcript_id"], "123")
