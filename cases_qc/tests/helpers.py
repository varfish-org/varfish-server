import datetime
import json
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


def determined_words(*args, **kwargs):
    res = mock.Mock()
    res.side_effect = (f"word{i}" for i in range(10000))
    return res


class FlattenEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def flatten_via_json(data: dict) -> dict:
    """Flatten a dictionary by converting it to JSON and back."""
    return json.loads(json.dumps(data, cls=FlattenEncoder))
