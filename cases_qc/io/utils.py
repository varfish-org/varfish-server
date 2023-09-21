import typing


def try_cast(
    value: str,
    types: typing.Iterable[typing.Type],
    none_values: typing.Iterable[typing.Any] = (None, "", "NA", ".", "inf"),
) -> typing.Union[str, int, float, None]:
    if value in none_values and None in types:
        return None

    for type in types:
        if type is not None:
            try:
                return type(value)
            except ValueError:
                continue
    if None in types:
        return None
    else:
        raise ValueError(f"could not cast value {value} to any of {types}")
