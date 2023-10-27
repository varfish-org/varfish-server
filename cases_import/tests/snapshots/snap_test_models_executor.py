# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["BuildLegacyModelTest::test_build_legacy_pedigree legacy pedigree for family.yaml"] = [
    {
        "affected": 2,
        "father": "father",
        "has_gt_entries": True,
        "mother": "mother",
        "patient": "index",
        "sex": 1,
    },
    {
        "affected": 1,
        "father": "0",
        "has_gt_entries": True,
        "mother": "0",
        "patient": "father",
        "sex": 1,
    },
    {
        "affected": 1,
        "father": "0",
        "has_gt_entries": True,
        "mother": "0",
        "patient": "mother",
        "sex": 2,
    },
]

snapshots["ImportCreateWithSeqvarVcfTest::test_run external files"] = [
    {
        "available": None,
        "designation": "variant_calls",
        "file_attributes": {
            "checksum": "sha256:4042c2afa59f24a327b3852bfcd0d8d991499d9c4eb81e7a7efe8d081e66af82",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "text/plain+x-bgzip+x-variant-call-format",
            "variant_type": "seqvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "file://cases_import/tests/data/sample-brca1.vcf.gz",
    },
    {
        "available": None,
        "designation": "variant_calls",
        "file_attributes": {
            "checksum": "sha256:6b137335b7803623c3389424e7b64d704fb1c9f3f55792db2916d312e2da27ef",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "application/octet-stream+x-tabix-tbi-index",
            "variant_type": "seqvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "file://cases_import/tests/data/sample-brca1.vcf.gz.tbi",
    },
]

snapshots["ImportCreateWithSeqvarVcfTest::test_run internal files"] = [
    {
        "checksum": None,
        "designation": "variant_calls/seqvars/orig-copy",
        "file_attributes": {
            "checksum": "sha256:4042c2afa59f24a327b3852bfcd0d8d991499d9c4eb81e7a7efe8d081e66af82",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "text/plain+x-bgzip+x-variant-call-format",
            "variant_type": "seqvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/external-copy.vcf.gz",
    },
    {
        "checksum": None,
        "designation": "variant_calls/seqvars/ingested-vcf",
        "file_attributes": {},
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/ingested.vcf.gz",
    },
    {
        "checksum": None,
        "designation": "variant_calls/seqvars/ingested-tbi",
        "file_attributes": {},
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/ingested.vcf.gz.tbi",
    },
    {
        "checksum": None,
        "designation": "variant_calls/seqvars/prefiltered-vcf",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.05, "max_exon_dist": 1000, "prefilter_path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-0.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-0.vcf.gz",
    },
    {
        "checksum": None,
        "designation": "variant_calls/seqvars/prefiltered-vcf",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.01, "max_exon_dist": 100, "prefilter_path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-1.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-1.vcf.gz",
    },
    {
        "checksum": None,
        "designation": "variant_calls/seqvars/prefiltered-tbi",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.05, "max_exon_dist": 1000, "prefilter_path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-0.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-0.vcf.gz.tbi",
    },
    {
        "checksum": None,
        "designation": "variant_calls/seqvars/prefiltered-tbi",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.01, "max_exon_dist": 100, "prefilter_path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-1.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/7a/1d7b28-2bf8-4340-81f3-5487d86c669f/c28a70a6-1c75-40a1-8d89-216ca16cffca/seqvar/prefiltered-1.vcf.gz.tbi",
    },
]
