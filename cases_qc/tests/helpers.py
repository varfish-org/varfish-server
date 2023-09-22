import typing
from unittest import mock
import uuid


def extract_from_dict(vals: typing.Any, keys: typing.Iterable[str]) -> dict[str, typing.Any]:
    """Helper to extract certain values from the dictionary."""
    return {key: value for key, value in vars(vals).items() if key in keys}


def determined_uuids(*args, **kwargs):
    res = mock.Mock()
    res.side_effect = (
        uuid.UUID(f"00000000-0000-4000-8000-{i:012}", version=4) for i in range(10000)
    )
    return res
