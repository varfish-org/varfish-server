"""Tests for the admin command implementations in ``cmds``."""

import io
import pathlib
import sys
import types
import uuid

from django.test import TestCase

from ..cmds import CollectionDeleteImpl, CollectionImportImpl, CollectionListImpl
from ..models import RegElement, RegElementType, RegInteraction, RegMap, RegMapCollection
from .factories import RegMapCollectionFactory


class CollectionListImplTest(TestCase):
    """Tests for CollectionListImpl"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def testListEmpty(self):
        f = io.StringIO()
        CollectionListImpl().run(f)
        expected = [
            "UUID                                    	title",
            "",
            "Total regulatory map collections: 0",
            "",
        ]
        self.assertEqual("\n".join(expected), f.getvalue())

    def testListWithOne(self):
        RegMapCollectionFactory(
            sodar_uuid=uuid.UUID("8526bea5-3f2a-4374-874d-5971e1ffbd4d"), title="This is something"
        )
        f = io.StringIO()
        CollectionListImpl().run(f)
        expected = [
            "UUID                                    	title",
            "8526bea5-3f2a-4374-874d-5971e1ffbd4d    	This is something",
            "",
            "Total regulatory map collections: 1",
            "",
        ]
        self.assertEqual("\n".join(expected), f.getvalue())


class CollectionDeleteImplTest(TestCase):
    """Tests for CollectionDeleteImpl"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def testDelete(self):
        coll = RegMapCollectionFactory()
        self.assertEqual(RegMapCollection.objects.count(), 1)
        CollectionDeleteImpl(uuid=str(coll.sodar_uuid)).run()
        self.assertEqual(RegMapCollection.objects.count(), 0)


class CollectionImportImplTest(TestCase):
    """Tests for CollectionImportImpl"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def testImport(self):
        path = pathlib.Path(__file__).parent / "ex_coll"
        style = types.SimpleNamespace(SUCCESS=lambda x: x)
        f = io.StringIO()
        CollectionImportImpl(path=str(path), stderr=f, style=style).run()

        keys = ["title", "short_title", "slug", "version"]
        vals = [{k: v[k] for k in keys} for v in map(vars, RegMapCollection.objects.all())]
        expected = [
            {
                "short_title": "Example (Holtgrewe 2020)",
                "slug": "varfish_example",
                "title": "Example Regulatory Map Collection",
                "version": "v0.0.20201022",
            }
        ]
        self.assertEquals(expected, vals)

        keys = ["title", "short_title", "slug"]
        vals = [{k: v[k] for k in keys} for v in map(vars, RegMap.objects.all())]
        expected = [{"short_title": "Macrophages", "slug": "MA", "title": "Macrophages"}]
        self.assertEquals(expected, vals)

        keys = ["title", "short_title", "slug"]
        vals = [{k: v[k] for k in keys} for v in map(vars, RegElementType.objects.all())]
        expected = [
            {"short_title": "Enhancer", "slug": "enhancer", "title": "Enhancer"},
            {"short_title": "Promoter", "slug": "promoter", "title": "Promoter"},
        ]
        self.assertEquals(expected, vals)

        keys = [
            "release",
            "chromosome",
            "start",
            "end",
            "elem_type_id",
            "score",
        ]
        vals = [{k: v[k] for k in keys} for v in map(vars, RegElement.objects.all())]
        expected = [
            {
                "chromosome": "1",
                "elem_type_id": vals[0]["elem_type_id"],
                "end": 123456,
                "release": "GRCh37",
                "score": 1.0,
                "start": 123124,
            },
            {
                "chromosome": "1",
                "elem_type_id": vals[1]["elem_type_id"],
                "end": 223456,
                "release": "GRCh37",
                "score": 1.0,
                "start": 223124,
            },
        ]
        self.assertEquals(expected, vals)

        keys = [
            "release",
            "chromosome",
            "start",
            "end",
            "score",
            "chromosome1",
            "start1",
            "end1",
            "chromosome2",
            "start2",
            "end2",
            "extra_data",
        ]
        vals = [{k: v[k] for k in keys} for v in map(vars, RegInteraction.objects.all())]
        expected = [
            {
                "chromosome": "1",
                "chromosome1": "1",
                "chromosome2": "1",
                "end": 223456,
                "end1": 123456,
                "end2": 223456,
                "extra_data": {"key": "value"},
                "release": "GRCh37",
                "score": 1.0,
                "start": 123124,
                "start1": 123124,
                "start2": 223124,
            }
        ]
        self.assertEquals(expected, vals)
