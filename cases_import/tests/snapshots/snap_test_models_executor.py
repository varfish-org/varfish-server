# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots["ImportCreateWithSeqvarVcfTest::test_run external files"] = [
    {
        "available": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 488009, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 488021, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls",
        "file_attributes": {
            "checksum": "sha256:4042c2afa59f24a327b3852bfcd0d8d991499d9c4eb81e7a7efe8d081e66af82",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "text/plain+x-bgzip+x-variant-call-format",
            "variant_type": "seqvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "last_checked": None,
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "file://cases_import/tests/data/sample-brca1.vcf.gz",
    },
    {
        "available": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 488657, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 488669, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls",
        "file_attributes": {
            "checksum": "sha256:6b137335b7803623c3389424e7b64d704fb1c9f3f55792db2916d312e2da27ef",
            "designation": "variant_calls",
            "genomebuild": "grch37",
            "mimetype": "application/octet-stream+x-tabix-tbi-index",
            "variant_type": "seqvars",
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "last_checked": None,
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "file://cases_import/tests/data/sample-brca1.vcf.gz.tbi",
    },
]

snapshots["ImportCreateWithSeqvarVcfTest::test_run internal files"] = [
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 824401, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 824419, tzinfo=<UTC>)"
        ),
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
        "path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/external-copy.vcf.gz",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 828810, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 828838, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/ingested-vcf",
        "file_attributes": {},
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/ingested.vcf.gz",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 829572, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 829584, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/ingested-tbi",
        "file_attributes": {},
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/ingested.vcf.gz.tbi",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 832143, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 832159, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/prefiltered-vcf",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.05, "max_exon_dist": 1000, "prefilter_path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-0.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-0.vcf.gz",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 832824, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 832836, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/prefiltered-vcf",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.01, "max_exon_dist": 100, "prefilter_path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-1.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-1.vcf.gz",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 833415, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 833426, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/prefiltered-tbi",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.05, "max_exon_dist": 1000, "prefilter_path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-0.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-0.vcf.gz.tbi",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 834024, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 13, 26, 50, 834036, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/prefiltered-tbi",
        "file_attributes": {
            "prefilter_config": '{"max_freq": 0.01, "max_exon_dist": 100, "prefilter_path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-1.vcf.gz"}'
        },
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/fa/59725d-4acc-4734-aa91-3834ab483f77/19d32d6f-7e9e-4e5a-a442-b2fb5ff8921b/seqvar/prefiltered-1.vcf.gz.tbi",
    },
]
