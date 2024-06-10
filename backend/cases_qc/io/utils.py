import re
import typing


def try_cast(
    value: str,
    types: typing.Iterable[typing.Type],
    none_values: typing.Iterable[typing.Any] = (None, "", "NA", "n/a", ".", "inf"),
) -> typing.Union[str, int, float, None]:
    if value in none_values and None in types:
        return None

    for type_ in types:
        if type_ is not None:
            value = value.strip()  # strip whitespace
            if type_ is int and not re.match(r"^\d+$", value):
                continue  # int("1.1") works but we don't want that
            try:
                return type_(value)
            except ValueError:
                continue
    if None in types:
        return None
    else:
        raise ValueError(f"could not cast value {value} to any of {types}")
