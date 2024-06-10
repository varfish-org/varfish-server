import json
import re
from unittest.mock import patch

from django.forms import model_to_dict
import jsonmatch
from requests_mock import Mocker
from test_plus.test import TestCase

from genepanels.forms import GenePanelCategoryForm, GenePanelForm
from genepanels.models import GenePanel, GenePanelCategory, GenePanelEntry, GenePanelState
from genepanels.tests.factories import (
    GenePanelCategoryFactory,
    GenePanelEntryFactory,
    GenePanelFactory,
)
from genepanels.tests.test_views import ANNONARS_GENE_RESPONSE, AnnonarsMockerMixin
from variants.views import UUIDEncoder

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")


def my_model_to_dict(obj):
    """Convert model to dict and remove everything none-JSON"""
    return json.loads(json.dumps(model_to_dict(obj), cls=UUIDEncoder))


class TestGenePanelCategoryForm(TestCase):
    def test_empty_form(self):
        # test initialization without instance
        form = GenePanelCategoryForm()
        # test __str__()
        self.assertIn("Optional description of the category", str(form))

    def test_form_with_instance(self):
        # test initialization with instance
        category = GenePanelCategoryFactory()
        form = GenePanelCategoryForm(instance=category)
        # test __str__()
        self.assertIn("Optional description of the category", str(form))

    def test_create(self):
        form_data = {"title": "This is a category", "description": "This is my test description"}
        self.assertEqual(GenePanelCategory.objects.count(), 0)
        form = GenePanelCategoryForm(data=form_data)
        form.save()
        self.assertEqual(GenePanelCategory.objects.count(), 1)
        expected0 = jsonmatch.compile(
            {
                "id": int,
                "sodar_uuid": RE_UUID4,
                "description": "This is my test description",
                "title": "This is a category",
            }
        )
        expected0.assert_matches(my_model_to_dict(GenePanelCategory.objects.all()[0]))

    def test_update(self):
        category = GenePanelCategoryFactory()
        form_data = {"title": "This is a category", "description": "This is my test description"}
        self.assertEqual(GenePanelCategory.objects.count(), 1)
        form = GenePanelCategoryForm(instance=category, data=form_data)
        form.save()
        self.assertEqual(GenePanelCategory.objects.count(), 1)
        expected0 = jsonmatch.compile(
            {
                "id": int,
                "sodar_uuid": RE_UUID4,
                "description": "This is my test description",
                "title": "This is a category",
            }
        )
        expected0.assert_matches(my_model_to_dict(GenePanelCategory.objects.all()[0]))


class TestGenePanelForm(AnnonarsMockerMixin, TestCase):
    def test_empty_form(self):
        # test initialization without instance
        form = GenePanelForm()
        # test __str__()
        self.assertIn("Minor version of the gene panel (by identifier)", str(form))

    def test_form_with_instance(self):
        # test initialization with instance
        category = GenePanelFactory()
        form = GenePanelForm(instance=category)
        # test __str__()
        self.assertIn("Minor version of the gene panel (by identifier)", str(form))

    def test_create(self):
        category = GenePanelCategoryFactory()
        form_data = {
            "identifier": "yada.yada.yada",
            "state": GenePanelState.ACTIVE.value,  # will not be used
            "version_major": 1,
            "version_minor": 2,
            "category": str(category.sodar_uuid),
            "title": "This is the title",
            "description": "This is the description",
        }
        self.assertEqual(GenePanel.objects.count(), 0)
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        form = GenePanelForm(data=form_data)
        form.full_clean()
        form.save()
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        self.assertEqual(GenePanel.objects.count(), 1)
        expected0 = jsonmatch.compile(
            {
                "id": int,
                "sodar_uuid": RE_UUID4,
                "identifier": "yada.yada.yada",
                "state": GenePanelState.DRAFT.value,
                "version_major": 1,
                "version_minor": 2,
                "category": category.id,
                "title": "This is the title",
                "description": "This is the description",
                "signed_off_by": None,
            }
        )
        expected0.assert_matches(my_model_to_dict(GenePanel.objects.all()[0]))

    @patch("django.conf.settings.VARFISH_BACKEND_URL_ANNONARS", "https://annonars.com")
    @Mocker()
    def test_create_with_entries(self, mock):
        self._set_annonars_mocker(mock)
        category = GenePanelCategoryFactory()
        form_data = {
            "identifier": "yada.yada.yada",
            "state": GenePanelState.ACTIVE.value,  # will not be used
            "version_major": 1,
            "version_minor": 2,
            "category": str(category.sodar_uuid),
            "title": "This is the title",
            "description": "This is the description",
            "genes": "TTN\nGBA1",
        }
        self.assertEqual(GenePanel.objects.count(), 0)
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        form = GenePanelForm(data=form_data)
        form.full_clean()
        form.save()
        self.assertEqual(GenePanelEntry.objects.count(), 2)
        self.assertEqual(GenePanel.objects.count(), 1)
        self.assertEqual(
            ["GBA1", "TTN"],
            list(sorted([e.symbol for e in GenePanelEntry.objects.all()])),
        )

    def test_update(self):
        panel = GenePanelFactory(
            state=GenePanelState.DRAFT.value, signed_off_by=None, version_major=1, version_minor=1
        )
        category = panel.category
        form_data = {
            "identifier": "yada.yada.yada",
            "state": GenePanelState.ACTIVE.value,  # will not be used
            "version_major": 1,
            "version_minor": 1,
            "category": str(category.sodar_uuid),
            "title": "This is the title",
            "description": "This is the description",
        }
        self.assertEqual(GenePanel.objects.count(), 1)
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        form = GenePanelForm(instance=panel, data=form_data)
        form.full_clean()
        form.save()
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        self.assertEqual(GenePanel.objects.count(), 1)
        expected0 = jsonmatch.compile(
            {
                "id": int,
                "sodar_uuid": RE_UUID4,
                "identifier": "yada.yada.yada",
                "state": GenePanelState.DRAFT.value,
                "version_major": 1,
                "version_minor": 1,
                "category": category.id,
                "title": "This is the title",
                "description": "This is the description",
                "signed_off_by": None,
            }
        )
        expected0.assert_matches(my_model_to_dict(GenePanel.objects.all()[0]))

    def test_update_with_old_panel(self):
        panel = GenePanelFactory(
            state=GenePanelState.DRAFT.value, signed_off_by=None, version_major=1, version_minor=1
        )
        category = panel.category
        old_panel = GenePanelFactory(
            identifier=panel.identifier,
            state=GenePanelState.ACTIVE.value,
            version_major=2,
            version_minor=42,
            category=category,
        )
        form_data = {
            "identifier": panel.identifier,
            "state": GenePanelState.ACTIVE.value,  # will not be used
            "version_major": 1,
            "version_minor": 1,
            "category": str(category.sodar_uuid),
            "title": "This is the title",
            "description": "This is the description",
        }
        self.assertEqual(GenePanel.objects.count(), 2)
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        form = GenePanelForm(instance=panel, data=form_data)
        form.save()
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        self.assertEqual(GenePanel.objects.count(), 2)
        expected0 = jsonmatch.compile(
            {
                "id": int,
                "sodar_uuid": RE_UUID4,
                "identifier": panel.identifier,
                "state": GenePanelState.DRAFT.value,
                "version_major": old_panel.version_major,
                "version_minor": old_panel.version_minor + 1,
                "category": category.id,
                "title": "This is the title",
                "description": "This is the description",
                "signed_off_by": None,
            }
        )
        expected0.assert_matches(my_model_to_dict(GenePanel.objects.get(id=panel.id)))

    @patch("django.conf.settings.VARFISH_BACKEND_URL_ANNONARS", "https://annonars.com")
    @Mocker()
    def test_update_with_entries(self, mock):
        self._set_annonars_mocker(mock)
        panel = GenePanelFactory(
            state=GenePanelState.DRAFT.value, signed_off_by=None, version_major=1, version_minor=1
        )
        panel_entry = GenePanelEntryFactory(
            panel=panel,
            symbol=ANNONARS_GENE_RESPONSE["TTN"]["symbol"],
            hgnc_id=ANNONARS_GENE_RESPONSE["TTN"]["hgnc_id"],
            ensembl_id=ANNONARS_GENE_RESPONSE["TTN"]["ensembl_gene_id"],
            ncbi_id=ANNONARS_GENE_RESPONSE["TTN"]["ncbi_gene_id"],
        )
        category = panel.category
        form_data = {
            "identifier": "yada.yada.yada",
            "state": GenePanelState.ACTIVE.value,  # will not be used
            "version_major": 1,
            "version_minor": 1,
            "category": str(category.sodar_uuid),
            "title": "This is the title",
            "description": "This is the description",
            "genes": "TTN\nGBA1",
        }
        self.assertEqual(GenePanel.objects.count(), 1)
        self.assertEqual(GenePanelEntry.objects.count(), 1)
        form = GenePanelForm(instance=panel, data=form_data)
        form.full_clean()
        form.save()
        self.assertEqual(GenePanelEntry.objects.count(), 2)
        self.assertEqual(GenePanel.objects.count(), 1)
        self.assertEqual(GenePanelEntry.objects.filter(pk=panel_entry.pk).count(), 0)
        self.assertEqual(
            ["GBA1", "TTN"],
            list(sorted([e.symbol for e in GenePanelEntry.objects.all()])),
        )

    @patch("django.conf.settings.VARFISH_BACKEND_URL_ANNONARS", "https://annonars.com")
    @Mocker()
    def test_update_with_invalid_hgnc(self, mock):
        self._set_annonars_mocker_NONEXISTENT(mock)
        panel = GenePanelFactory(
            state=GenePanelState.DRAFT.value, signed_off_by=None, version_major=1, version_minor=1
        )
        category = panel.category
        form_data = {
            "identifier": "yada.yada.yada",
            "state": GenePanelState.ACTIVE.value,  # will not be used
            "version_major": 1,
            "version_minor": 1,
            "category": str(category.sodar_uuid),
            "title": "This is the title",
            "description": "This is the description",
            "genes": "TTN\nGBA1\nNONEXISTENT",
        }
        self.assertEqual(GenePanel.objects.count(), 1)
        form = GenePanelForm(instance=panel, data=form_data)
        form.full_clean()
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()
        self.assertEquals(form.errors, {"genes": ["NONEXISTENT"]})
