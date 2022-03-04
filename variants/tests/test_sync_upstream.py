"""Tests for the ``variants.sync_upstream`` module."""

import glob
import json
import os
from unittest.mock import patch

import requests_mock
from projectroles.constants import SODAR_CONSTANTS
from test_plus.test import TestCase

from variants import sync_upstream
from variants.tests.factories import (
    CaseWithVariantSetFactory,
    SyncCaseListBgJobFactory,
    RemoteSiteFactory,
)


def load_isa_tab(base_path):
    """Helper to load ISA-Tab data and return it as the SODAR API would."""
    result = {}
    for path in glob.glob("%s/%s/?_*.txt" % (os.path.dirname(__file__), base_path)):
        basename = os.path.basename(path)
        for key, prefix in (("assays", "a_"), ("studies", "s_")):
            if basename.startswith(prefix):
                with open(path, "rt") as inputf:
                    result.setdefault(key, {})[os.path.basename(path)] = {"tsv": inputf.read()}
                break
        else:  # if no break above
            if basename.startswith("i_"):
                with open(path, "rt") as inputf:
                    result["investigation"] = {
                        "path": os.path.basename(path),
                        "tsv": inputf.read(),
                    }
    return result


class TestCompareToUpstream(TestCase):
    def setUp(self):
        super().setUp()
        self.superuser = self.make_user("superuser")
        self.case, _, _ = CaseWithVariantSetFactory.get("small")
        self.project = self.case.project
        self.sync_bg_job = SyncCaseListBgJobFactory(project=self.project, user=self.superuser)
        self.maxDiff = None

    def testRunDifferences(self):
        upstream_pedigree = {
            "123": sync_upstream.PedigreeMember(
                family="FAM_123",
                name="123",
                father="0",
                mother="0",
                sex=1,
                affected=2,
                sample_name="123-N1",
            )
        }
        self.assertEqual(self.project.synccaseresultmessage_set.count(), 0)
        sync_upstream.compare_to_upstream(self.project, upstream_pedigree, self.sync_bg_job.bg_job)
        messages = [msg.message for msg in self.project.synccaseresultmessage_set.all()]
        expected = [
            "Upstream/SODAR donors not found in VarFish project: 123.",
            "Varfish project donors not found in upstream/SODAR: %s."
            % self.case.pedigree[0]["patient"].split("-", 1)[0],
        ]
        self.assertEqual(list(sorted(messages)), expected)

    def testRunNoDifferences(self):
        upstream_pedigree = {
            p["patient"].split("-", 1)[0]: sync_upstream.PedigreeMember(
                family="<ignored>",
                name=p["patient"].split("-", 1)[0],
                father=p["father"],
                mother=p["mother"],
                sex=p["sex"],
                affected=p["affected"],
                sample_name=p["patient"].split("-", 1)[0],
            )
            for p in self.case.pedigree
        }
        self.assertEqual(self.project.synccaseresultmessage_set.count(), 0)
        sync_upstream.compare_to_upstream(self.project, upstream_pedigree, self.sync_bg_job.bg_job)
        messages = [msg.message for msg in self.project.synccaseresultmessage_set.all()]
        self.assertEqual(messages, [])


class TestFetchRemotePedigree(TestCase):
    def setUp(self):
        super().setUp()
        self.case, _, _ = CaseWithVariantSetFactory.get("small")
        self.project = self.case.project
        self.remote_site = RemoteSiteFactory()
        self.isa_tab_json = json.dumps(load_isa_tab("data/isa_tab_singleton"))
        self.maxDiff = None

    @requests_mock.Mocker()
    def testRun(self, r_mock):
        r_mock.get(
            "%s/samplesheets/api/remote/get/%s/%s?isa=1"
            % (self.remote_site.url, self.project.sodar_uuid, self.remote_site.secret,),
            status_code=200,
            text=self.isa_tab_json,
        )
        result = sync_upstream.fetch_remote_pedigree(self.remote_site, self.project)
        expected = {
            "index": sync_upstream.PedigreeMember(
                family="FAM_index",
                name="index",
                father="0",
                mother="0",
                sex=1,
                affected=2,
                sample_name="index-N1",
                hpo_terms=["HP:0000939", "HP:0011002"],
                orphanet_diseases=["ORPHA:2781", "ORPHA:2788"],
                omim_diseases=["OMIM:166710"],
            )
        }
        self.assertEqual(result, expected)


class TestExecuteSyncCaseListJob(TestCase):
    def setUp(self):
        super().setUp()
        self.superuser = self.make_user("superuser")
        self.case, _, _ = CaseWithVariantSetFactory.get("small")
        self.project = self.case.project
        self.remote_site = RemoteSiteFactory(mode=SODAR_CONSTANTS["SITE_MODE_SOURCE"])
        self.sync_bg_job = SyncCaseListBgJobFactory(project=self.project, user=self.superuser)
        self.maxDiff = None

    def testRunDifferences(self):
        upstream_pedigree = {
            "123": sync_upstream.PedigreeMember(
                family="FAM_123",
                name="123",
                father="0",
                mother="0",
                sex=1,
                affected=2,
                sample_name="123-N1",
            )
        }
        self.assertEqual(self.project.synccaseresultmessage_set.count(), 0)
        with patch("variants.sync_upstream.fetch_remote_pedigree", return_value=upstream_pedigree):
            sync_upstream.execute_sync_case_list_job(self.sync_bg_job)
            messages = [msg.message for msg in self.project.synccaseresultmessage_set.all()]
            expected = [
                "Upstream/SODAR donors not found in VarFish project: 123.",
                "Varfish project donors not found in upstream/SODAR: %s."
                % self.case.pedigree[0]["patient"].split("-", 1)[0],
            ]
            self.assertEqual(list(sorted(messages)), expected)

    def testRunNoDifferences(self):
        upstream_pedigree = {
            p["patient"].split("-", 1)[0]: sync_upstream.PedigreeMember(
                family="<ignored>",
                name=p["patient"].split("-", 1)[0],
                father=p["father"],
                mother=p["mother"],
                sex=p["sex"],
                affected=p["affected"],
                sample_name=p["patient"].split("-", 1)[0],
            )
            for p in self.case.pedigree
        }
        self.assertEqual(self.project.synccaseresultmessage_set.count(), 0)
        with patch("variants.sync_upstream.fetch_remote_pedigree", return_value=upstream_pedigree):
            sync_upstream.execute_sync_case_list_job(self.sync_bg_job)
            messages = [msg.message for msg in self.project.synccaseresultmessage_set.all()]
            self.assertEqual(messages, [])
