import enum
import typing

import pydantic


class MehariGenomeRelease(str, enum.Enum):
    Grch37 = "grch37"
    Grch38 = "grch38"


class MehariPosition(pydantic.BaseModel, frozen=True):
    ord: int
    total: typing.Optional[int]


class MehariSeqVarResult(pydantic.BaseModel, frozen=True):
    consequences: typing.List[str]
    putative_impact: str
    gene_symbol: str
    gene_id: str
    feature_type: dict
    feature_id: str
    feature_biotype: str
    rank: typing.Optional[dict]
    hgvs_t: typing.Optional[str]
    hgvs_p: typing.Optional[str]
    tx_pos: typing.Optional[MehariPosition]
    cds_pos: typing.Optional[MehariPosition]
    protein_pos: typing.Optional[MehariPosition]
    distance: typing.Optional[int]
    messages: typing.Optional[typing.List[str]]


class MehariSeqVarQuery(pydantic.BaseModel, frozen=True):
    genome_release: MehariGenomeRelease
    chromosome: str
    position: int
    reference: str
    alternative: str
    hgnc_id: typing.Optional[str]


class MehariSeqVarResponse(pydantic.BaseModel, frozen=True):
    version: dict
    query: dict
    result: typing.List[MehariSeqVarResult]
