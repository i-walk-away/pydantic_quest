from __future__ import annotations

import re

LESSON_ORDER_PATTERN = re.compile(r"^[1-9]\d*(?:\.[1-9]\d*)*$")


def normalize_lesson_order(value: str | int | float) -> str:
    """
    Normalize lesson order into a dotted numeric path string.

    :param value: raw lesson order

    :return: normalized order
    """
    if isinstance(value, int):
        if value < 1:
            message = "order must be a positive dotted path like 1 or 2.3."
            raise ValueError(message)

        return str(value)

    if isinstance(value, float):
        if value < 1:
            message = "order must be a positive dotted path like 1 or 2.3."
            raise ValueError(message)

        return normalize_lesson_order(value=format(value, "g"))

    normalized = value.strip()
    if not LESSON_ORDER_PATTERN.fullmatch(normalized):
        message = "order must be a positive dotted path like 1 or 2.3."
        raise ValueError(message)

    return normalized


def lesson_order_key(value: str | int | float) -> tuple[int, ...]:
    """
    Convert lesson order into a sortable tuple.

    :param value: raw lesson order

    :return: tuple of numeric order parts
    """
    normalized = normalize_lesson_order(value=value)

    return tuple(int(part) for part in normalized.split("."))
