import typing

import requests

from .models import mehari


class MehariSeqVarApi:
    csq_url = "/seqvars/csq"

    def __init__(self, base_url: str):
        self._base_url = base_url

    def csq(self, query: mehari.MehariSeqVarQuery) -> mehari.MehariSeqVarResult:
        query_dict = query.dict()
        resp = requests.get(self._base_url + self.csq_url, params=query_dict)
        resp.raise_for_status()
        result = mehari.MehariSeqVarResponse(**resp.json())
        return result

    def get_variant(
        self, genome_release: str, chromosome: str, position: str, reference: str, alternative: str
    ) -> typing.Optional[mehari.MehariSeqVarResult]:
        return self.csq(
            mehari.MehariSeqVarQuery(
                genome_release=genome_release,
                chromosome=chromosome,
                position=position,
                reference=reference,
                alternative=alternative,
            )
        )
