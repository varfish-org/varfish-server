"""Test for the ``submit_mehari`` module."""

import requests_mock
from test_plus.test import TestCase

from svs.submit_mehari import MehariStrucVarApi
from svs.models.mehari import MehariStrucVarQuery, MehariStrucVarResponse


class MehariSubmitTests(TestCase):
    @requests_mock.Mocker()
    def test_submit_variant(self, mock_):
        query = MehariStrucVarQuery(
            **{
                "genome_release": "grch37",
                "chromosome": "17",
                "start": 48275363,
                "stop": "48275374",
                "sv_type": "DEL",
            }
        )
        expected = MehariStrucVarResponse(
            **{
                "version": {"tx_db": "0.5.0", "mehari": "0.11.0"},
                "query": query.dict(),
                "result": [
                    {
                        "hgnc_id": "HGNC:2197",
                        "transcript_effects": ["exon_variant", "splice_region_variant", "intron_variant"]
                    }
                ],
            }
        )
        base_url = "http://testmehari"
        mock_.get(
            base_url + MehariStrucVarApi.csq_url,
            json=expected.dict(),
        )

        mehari = MehariStrucVarApi(base_url)
        result = mehari.csq(query)
        self.assertEqual(result, expected)
