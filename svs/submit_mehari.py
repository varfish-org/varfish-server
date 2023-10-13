import typing

import requests

from .models import mehari


class MehariStrucVarApi:
    csq_url = "/strucvars/csq"

    def __init__(self, base_url: str):
        self._base_url = base_url

    def csq(self, query: mehari.MehariStrucVarQuery) -> mehari.MehariStrucVarResponse:
        query_dict = query.dict()
        resp = requests.get(self._base_url + self.csq_url, params=query_dict)
        resp.raise_for_status()
        result = mehari.MehariStrucVarResponse(**resp.json())
        return result

    def get_variant(
        self, genome_release: str, chromosome: str, start: str, stop: str, sv_type: str
    ) -> typing.Optional[mehari.MehariStrucVarResponse]:
        return self.csq(
            mehari.MehariStrucVarQuery(
                genome_release=genome_release,
                chromosome=chromosome,
                start=start,
                stop=stop,
                sv_type=sv_type,
            )
        )
