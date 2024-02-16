"""Test for the ``submit_mehari`` module."""

import requests_mock
from test_plus.test import TestCase

from variants import submit_mehari
from variants.models.mehari import MehariSeqVarQuery, MehariSeqVarResponse


class MehariSubmitTests(TestCase):
    @requests_mock.Mocker()
    def test_submit_variant(self, mock_):
        query = MehariSeqVarQuery(
            **{
                "genome_release": "grch37",
                "chromosome": "17",
                "position": 48275363,
                "reference": "C",
                "alternative": "A",
            }
        )
        expected = MehariSeqVarResponse(
            **{
                "version": {"tx_db": "0.5.0", "mehari": "0.11.0"},
                "query": {
                    "genome_release": "grch37",
                    "chromosome": "17",
                    "position": 48275363,
                    "reference": "C",
                    "alternative": "A",
                    "hgnc_id": None,
                },
                "result": [
                    {
                        "consequences": ["MissenseVariant", "SpliceRegionVariant"],
                        "putative_impact": "Moderate",
                        "gene_symbol": "COL1A1",
                        "gene_id": "HGNC:2197",
                        "feature_type": {"SoTerm": {"term": "Transcript"}},
                        "feature_id": "NM_000088.4",
                        "feature_biotype": "Coding",
                        "rank": {"ord": 8, "total": 51},
                        "hgvs_t": "c.589G>T",
                        "hgvs_p": "p.G197C",
                        "tx_pos": {"ord": 707, "total": 5914},
                        "cds_pos": {"ord": 589, "total": 4395},
                        "protein_pos": {"ord": 197, "total": 1465},
                        "distance": 0,
                        "messages": None,
                    }
                ],
            }
        )
        base_url = "http://testmehari"
        mock_.get(
            base_url + submit_mehari.MehariSeqVarApi.csq_url,
            json=expected.dict(),
        )

        mehari = submit_mehari.MehariSeqVarApi(base_url)
        result = mehari.csq(query)
        self.assertEqual(result, expected)
