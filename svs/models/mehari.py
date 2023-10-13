import enum
import typing

import pydantic

from variants.models.mehari import MehariGenomeRelease, MehariPosition


class MehariStrucVarResult(pydantic.BaseModel, frozen=True):
    hgnc_id: str
    transcript_effects: typing.List[str]


class MehariStrucVarQuery(pydantic.BaseModel, frozen=True):
    genome_release: MehariGenomeRelease
    chromosome: str
    start: int
    stop: int
    sv_type: str


class MehariStrucVarResponse(pydantic.BaseModel, frozen=True):
    version: dict
    query: dict
    result: typing.List[MehariStrucVarResult]
