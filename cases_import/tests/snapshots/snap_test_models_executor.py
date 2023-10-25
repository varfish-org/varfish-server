# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots["ImportCreateWithSeqvarVcfTest::test_run external files"] = [
    {
        "available": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 499829, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 499842, tzinfo=<UTC>)"
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
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 500613, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 500625, tzinfo=<UTC>)"
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
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 791638, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 791679, tzinfo=<UTC>)"
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
        "path": "case-data/63/517f2b-34f9-481e-bfe0-91f0d702adae/0ab5c70a-caab-473e-9210-ff030d19b8b6/seqvar/external-copy.vcf.gz",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 795019, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 795034, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/ingested-vcf",
        "file_attributes": {},
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "text/plain+x-bgzip+x-variant-call-format",
        "path": "case-data/63/517f2b-34f9-481e-bfe0-91f0d702adae/0ab5c70a-caab-473e-9210-ff030d19b8b6/seqvar/ingested.vcf.gz",
    },
    {
        "checksum": None,
        "date_created": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 795757, tzinfo=<UTC>)"
        ),
        "date_modified": GenericRepr(
            "datetime.datetime(2023, 10, 25, 12, 30, 41, 795771, tzinfo=<UTC>)"
        ),
        "designation": "variant_calls/seqvars/ingested-tbi",
        "file_attributes": {},
        "identifier_map": {"index": "NA12878-PCRF450-1"},
        "mimetype": "application/octet-stream+x-tabix-tbi-index",
        "path": "case-data/63/517f2b-34f9-481e-bfe0-91f0d702adae/0ab5c70a-caab-473e-9210-ff030d19b8b6/seqvar/ingested.vcf.gz.tbi",
    },
]
