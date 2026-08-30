"""Canonical power unit is the watt. Display helpers convert at the edge."""

WATTS_PER_KILOWATT = 1_000

_SUFFIXES = {
    "w": 1,
    "watt": 1,
    "watts": 1,
    "kw": WATTS_PER_KILOWATT,
    "kilowatt": WATTS_PER_KILOWATT,
    "kilowatts": WATTS_PER_KILOWATT,
}


def watts_from_label(value: object) -> int:
    """Parse an int of watts, or a string like '112 kW' / '112000 W'."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a power value")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("power cannot be negative")
        return value
    if isinstance(value, float):
        if value < 0 or not value.is_integer():
            raise ValueError("power must be a non-negative whole number of watts")
        return int(value)
    if not isinstance(value, str):
        raise ValueError(f"unsupported power value: {value!r}")

    text = value.strip().lower().replace(",", "")
    if not text:
        raise ValueError("empty power value")
    parts = text.split()
    if len(parts) == 1:
        number, suffix = _split_compact(parts[0])
    elif len(parts) == 2:
        number, suffix = parts[0], parts[1]
    else:
        raise ValueError(f"unrecognized power value: {value!r}")
    try:
        amount = float(number)
    except ValueError as exc:
        raise ValueError(f"unrecognized power value: {value!r}") from exc
    if amount < 0 or not amount.is_integer():
        raise ValueError("power must be a non-negative whole number of watts")
    factor = _SUFFIXES.get(suffix)
    if factor is None:
        raise ValueError(f"unknown power unit {suffix!r}")
    return int(amount) * factor


def _split_compact(token: str) -> tuple[str, str]:
    i = 0
    while i < len(token) and (token[i].isdigit() or token[i] == "."):
        i += 1
    if i == 0 or i == len(token):
        raise ValueError(f"unrecognized power value: {token!r}")
    return token[:i], token[i:]


def format_kw(watts: int) -> str:
    if watts % WATTS_PER_KILOWATT == 0:
        return f"{watts // WATTS_PER_KILOWATT} kW"
    return f"{watts / WATTS_PER_KILOWATT:.3f} kW"
