from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field, computed_field

from ..utils import snowflake_time


__all__ = ("Snowflake",)


class Snowflake(BaseModel):
    """Data model for snowflake objects."""

    id: Annotated[int, Field(description="The snowflake ID")]

    @computed_field  # type: ignore[misc]
    @property
    def created_at(self) -> datetime:
        """The time at which this snowflake was created"""
        return snowflake_time(self.id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Snowflake):
            return self.id == other.id

        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, Snowflake):
            return self.id != other.id

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)
