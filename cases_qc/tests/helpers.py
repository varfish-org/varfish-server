import typing


def extract_from_dict(vals: typing.Any, keys: typing.Iterable[str]) -> dict[str, typing.Any]:
    """Helper to extract certain values from the dictionary."""
    return {key: value for key, value in vars(vals).items() if key in keys}
