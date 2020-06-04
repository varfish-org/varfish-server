"""Models for typed represetation of the JSON in the clinvar records.

Identical to the records in ``clinvar-tsv`` without parsing from XML.
"""

import datetime
import json

import attr
import cattr
from dateutil.parser import isoparse
import typing


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)


TClinicalSignificance = typing.TypeVar("ClinicalSignificance")
TReferenceClinVarAssertion = typing.TypeVar("ReferenceClinVarAssertion")
TClinVarSet = typing.TypeVar("ClinVarSet")


@attr.s(frozen=True, auto_attribs=True)
class ClinicalSignificance:
    """Represent clinical significance."""

    #: Date of last evaluation.
    date_evaluated: datetime.date
    #: Significance review status.
    review_status: str
    #: Significance description.
    description: str
    #: Comments.
    comments: typing.Tuple[str, ...]


@attr.s(frozen=True, auto_attribs=True)
class ObservedDataDescription:
    """Relevant information from ObservedData/Attribute[@Type='Description']."""

    #: Optional description text.
    description: typing.Optional[str]
    #: PubMed IDs.
    pubmed_ids: typing.Tuple[int]
    #: OMIM IDs.
    omim_ids: typing.Tuple[int]


@attr.s(frozen=True, auto_attribs=True)
class ObservedIn:
    """Relevant part of ObservedIn."""

    #: The origin of the sample.
    origin: str
    #: The species of the sample.
    species: str
    #: Affected state
    affected_status: str
    #: Optional observation info.
    observed_data_description: typing.Optional[ObservedDataDescription]
    #: Comments.
    comments: typing.Tuple[str, ...]


@attr.s(frozen=True, auto_attribs=True)
class SequenceLocation:
    """The relevant information from a SequenceLocation."""

    assembly: str
    chrom: str
    chrom_acc: str
    start: typing.Optional[int]
    stop: typing.Optional[int]
    outer_start: typing.Optional[int]
    outer_stop: typing.Optional[int]
    inner_start: typing.Optional[int]
    inner_stop: typing.Optional[int]
    ref: typing.Optional[str]
    alt: typing.Optional[str]


@attr.s(frozen=True, auto_attribs=True)
class Measure:
    """Represent the relevant informatino from a Measure."""

    measure_type: str
    symbols: typing.Tuple[str]
    hgnc_ids: typing.Tuple[str]
    sequence_locations: typing.Dict[str, SequenceLocation]
    comments: typing.Tuple[str, ...]


@attr.s(frozen=True, auto_attribs=True)
class Trait:
    """Represent the relevant information from a Trait."""

    preferred_name: typing.Optional[str]
    alternate_names: typing.Tuple[str, ...]


@attr.s(frozen=True, auto_attribs=True)
class TraitSet:
    """Represent the relevant information from a TraitSet."""

    #: Value of the "Type" attribute.
    set_type: str
    #: Numeric id_no for the ClinVarSet.
    id_no: typing.Optional[int]
    #: The traits in the set.
    traits: typing.Tuple[Trait, ...]


@attr.s(frozen=True, auto_attribs=True)
class MeasureSet:
    """Represent the relevant information from a MeasureSet."""

    set_type: str
    accession: str
    measures: typing.Tuple[Measure, ...]


@attr.s(frozen=True, auto_attribs=True)
class GenotypeSet:
    """Represents a genotype observation in ClinVar.
    NB: we introduce dummy sets even for non-compound variants.
    """

    set_type: str
    accession: str
    measure_sets: typing.Tuple[MeasureSet, ...]


@attr.s(frozen=True, auto_attribs=True)
class ReferenceClinVarAssertion:
    """Represent the relevant parts of a ReferenceClinVarAssertion."""

    #: Numeric id_no for the ClinVarSet.
    id_no: int
    #: Record status
    record_status: str
    #: Date of creation.
    date_created: datetime.date
    #: Date of last update.
    date_updated: datetime.date

    #: The accession number.
    clinvar_accession: str
    #: The version of the record.
    version_no: int
    #: Description where the variant was observed.
    observed_in: typing.Optional[ObservedIn]
    #: Genotype sets
    genotype_sets: typing.Tuple[GenotypeSet, ...]
    #: Trait sets.
    trait_sets: typing.Tuple[TraitSet, ...]
    #: Clinical significance entries.
    clin_sigs: typing.Tuple[ClinicalSignificance]

    #: Number of gold stars show on ClinVar.
    gold_stars: int
    #: Review status
    review_status: str
    #: Assertion of pathogenicity.
    pathogenicity: str


@attr.s(frozen=True, auto_attribs=True)
class ClinVarAssertion:
    """Represent the relevant parts of a ClinVarAssertion."""

    #: Numeric id_no for the ClinVarSet.
    id_no: int
    #: Record status
    record_status: str
    #: Date of submission.
    submitter_date: typing.Optional[datetime.date]

    #: The accession number.
    clinvar_accession: str
    #: The version of the record.
    version_no: int
    #: Description where the variant was observed.
    observed_in: typing.Optional[ObservedIn]
    #: Genotype sets
    genotype_sets: typing.Tuple[GenotypeSet, ...]
    #: Trait sets.
    trait_sets: typing.Tuple[TraitSet, ...]


@attr.s(frozen=True, auto_attribs=True)
class ClinVarSet:
    """Represent the relevant parts of a ClinVarSet."""

    #: Numeric id_no for the ClinVarSet.
    id_no: int
    #: Record status
    record_status: str
    #: Record title
    title: str
    #: The ReferenceClinVarAssertion, if any.
    ref_cv_assertion: typing.Optional[ReferenceClinVarAssertion]
    #: The ClinVarAssertion objects, if any.
    cv_assertions: typing.Tuple[ClinVarAssertion, ...]

    @classmethod
    def from_json(cls, json: typing.Any):
        return cattr.structure(json, ClinVarSet)
