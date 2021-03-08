import typing

import attr


#: Default assembly ID to assume.
DEFAULT_ASSEMBLY_ID = "GRCh37"
#: Indicated API version.
API_VERSION = "v1.0.0"


@attr.s(frozen=True, auto_attribs=True)
class Error:
    errorCode: int
    errorMessage: str


@attr.s(frozen=True, auto_attribs=True)
class BeaconAlleleRequest:
    referenceName: str
    referenceBases: str
    start: int
    alternateBases: str
    assemblyId: str = DEFAULT_ASSEMBLY_ID


@attr.s(frozen=True, auto_attribs=True)
class DatasetAlleleResponse:
    datasetId: str
    exists: typing.Optional[bool] = None
    error: typing.Optional[Error] = None
    frequency: typing.Optional[float] = None
    variantCount: typing.Optional[int] = None
    callCount: typing.Optional[int] = None
    sampleCount: typing.Optional[int] = None
    note: typing.Optional[str] = None
    externalUrl: typing.Optional[str] = None
    info: typing.Optional[typing.List[typing.Any]] = None


@attr.s(frozen=True, auto_attribs=True)
class BeaconAlleleResponse:
    beaconId: str
    apiVersion: str
    exists: bool
    alleleRequest: BeaconAlleleRequest
    datasetAlleleResponse: typing.Optional[typing.List[DatasetAlleleResponse]] = None
    error: typing.Optional[Error] = None


@attr.s(frozen=True, auto_attribs=True)
class Organisation:
    id: str
    name: str
    description: str


@attr.s(frozen=True, auto_attribs=True)
class Dataset:
    id: str
    name: str
    assembly: str
    description: str = None


@attr.s(frozen=True, auto_attribs=True)
class BeaconInfo:
    id: str
    name: str
    apiVersion: str
    organisation: Organisation
    datasets: typing.Tuple[Dataset]
