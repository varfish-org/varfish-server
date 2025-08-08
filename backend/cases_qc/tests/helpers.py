import datetime
import json
import random
import typing
from unittest import mock
import uuid

import factory

# Import factories here so all classes have been declared here and we
# can reset their counters in ResetFactoryCountersMixin.
import cases.tests.factories  # noqa: F401
import cases_qc.tests.factories  # noqa: F401


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
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat(timepsec="seconds")
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def flatten_via_json(data: dict) -> dict:
    """Flatten a dictionary by converting it to JSON and back."""
    return json.loads(json.dumps(data, cls=FlattenEncoder))


def fake_urandom(size: int, /) -> bytes:
    """Fake version of urandom that uses random."""
    return bytes(random.randint(0, 255) for _ in range(size))


class FixRandomSeedMixin:
    def setUp(self):
        """Set fixed seeds."""
        super().setUp()
        # determine the seed
        seed = getattr(self, "__fixrandomseed_fixed_seed", 42)
        # seed the random module and keep state for recovery
        self._FixRandomSeedMixin__random_state = random.getstate()
        random.seed(seed)
        # patch all factory.Faker random states
        self._FixRandomSeedMixin__faker_generators = []
        default_faker = factory.Faker._get_faker()
        for the_factory in default_faker.factories:
            self._FixRandomSeedMixin__faker_generators.append(the_factory._Generator__random)
            the_factory._Generator__random = random.Random(seed)
        # patch the os.urandom function
        self._FixRandomSeedMixin_patcher = mock.patch("os.urandom", new=fake_urandom)
        self._FixRandomSeedMixin_patcher.start()

    def tearDown(self):
        """Reset the random state"""
        super().tearDown()
        # recover all factory.Faker random states
        default_faker = factory.Faker._get_faker()
        for the_factory, generator in zip(
            default_faker.factories, self._FixRandomSeedMixin__faker_generators
        ):
            the_factory._Generator__random = generator
        # recover the random module's state
        random.setstate(self._FixRandomSeedMixin__random_state)
        # recover the os.urandom function
        self._FixRandomSeedMixin_patcher.stop()


class ResetFactoryCountersMixin:
    def setUp(self):
        """Reset the factory counters."""
        super().setUp()
        self._reset_subclasses_of(factory.Factory)

    def _reset_subclasses_of(self, cls):
        for subcls in cls.__subclasses__():
            try:
                subcls.reset_sequence()
            except ValueError as e:
                if "Can't reset a sequence on descendant factory" in str(e):
                    pass  # swallow
                else:
                    raise  # re-raise
            self._reset_subclasses_of(subcls)
