from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta, timezone
from hashlib import sha512
from typing import Any, Callable, List, Optional, TypeVar, TYPE_CHECKING

from .config import EPOCH


__all__ = ()
T = TypeVar("T")


class SQLBuildHelper:

    __slots__ = ("__pre_query", "__post_query", "__conditions", "__values")
    if TYPE_CHECKING:
        __pre_query: str
        __post_query: str
        __conditions: List[str]
        __values: List[Any]

    def __init__(self, pre_query: str, post_query: str = "") -> None:
        self.__pre_query = pre_query
        self.__post_query = post_query
        self.__conditions = []
        self.__values = []

    def add_condition(self, condition: str, value: Any, *, not_null_param: bool = True) -> SQLBuildHelper:
        if not_null_param and value is None:
            return self

        self.__conditions.append(f"({condition})")
        self.__values.append(value)
        return self

    def execute(self, func: Callable[..., T]) -> T:
        # Shallow copy `__values` as we may modify it
        values = self.__values.copy()

        parts = [self.__pre_query]
        if self.__conditions:
            parts.append("WHERE")
            parts.append(" AND ".join(self.__conditions))

        parts.append(self.__post_query)
        print("\n".join(parts), file=__import__("sys").stderr)
        print(values, file=__import__("sys").stderr)
        return func("\n".join(parts), *values)


def hash_password(password: str, *, salt: Optional[str] = None) -> str:
    """Hash a password using SHA-512 and a random salt."""
    if salt is None:
        salt = secure_hex_string(8)

    return sha512((password + salt).encode("utf-8")).hexdigest() + salt


def check_password(password: str, *, hashed: str) -> bool:
    """Check if a password matches a hashed password."""
    salt = hashed[-8:]
    return hashed == hash_password(password, salt=salt)


def secure_hex_string(length: int) -> str:
    """Generate a secure random hexadecimal string."""
    return "".join(secrets.choice(string.hexdigits) for _ in range(length))


def since_epoch(dt: Optional[datetime] = None) -> timedelta:
    """Get the timedelta since the epoch.

    Attributes
    -----
    dt: `Optional[datetime]`
        The datetime to calculate the timedelta from. If not provided, the current time is used.

    Returns
    -----
    `timedelta`
        The timedelta since the epoch: `dt - EPOCH`.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    return dt - EPOCH


def from_epoch(dt: timedelta) -> datetime:
    """Calculate the datetime from the timedelta since the epoch."""
    return EPOCH + dt


def snowflake_time(id: int) -> datetime:
    """Get the creation date of a snowflake ID."""
    return from_epoch(timedelta(milliseconds=id >> 16))
