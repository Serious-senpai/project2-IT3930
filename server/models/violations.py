from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from pydantic import Field
from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from .vehicles import Vehicle
from ..config import DB_PAGINATION_QUERY
from ..database import Database
from ..utils import SQLBuildHelper


__all__ = ("Violation",)


class Violation(Snowflake):
    """Represents a vehicle."""

    category: Annotated[Literal[0, 1, 2], Field(description="The violation category: 0 - speeding, 1 - red light, 2 - pavement")]
    fine_vnd: Annotated[int, Field(description="The fine amount in VND")]
    video_url: Annotated[str, Field(description="The URL to the video")]
    refutations_count: Annotated[int, Field(description="The number of refutations of this violation")]
    vehicle: Annotated[Vehicle, Field(description="The vehicle associated with this violation")]

    @classmethod
    def from_row(cls, row: Row) -> Violation:
        return cls(
            id=row.violation_id,
            category=row.violation_category,
            fine_vnd=row.violation_fine_vnd,
            video_url=row.violation_video_url,
            refutations_count=row.violation_refutations_count,
            vehicle=Vehicle.from_row(row),
        )

    @staticmethod
    async def query(
        violation_id: Optional[int] = None,
        violation_category: Optional[Literal[0, 1, 2]] = None,
        violation_fine_vnd: Optional[int] = None,
        violation_video_url: Optional[str] = None,
        violation_refutations_count: Optional[int] = None,
        vehicle_plate: Optional[str] = None,
        user_id: Optional[int] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
    ) -> List[Violation]:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                builder = SQLBuildHelper(
                    "SELECT * FROM view_violations",
                    f"ORDER BY violation_id DESC OFFSET 0 ROWS FETCH NEXT {DB_PAGINATION_QUERY} ROWS ONLY",
                ).add_condition(
                    "violation_id = ?",
                    violation_id,
                ).add_condition(
                    "violation_category = ?",
                    violation_category,
                ).add_condition(
                    "violation_fine_vnd = ?",
                    violation_fine_vnd,
                ).add_condition(
                    "violation_video_url LIKE ?",
                    violation_video_url,
                ).add_condition(
                    "violation_refutations_count = ?",
                    violation_refutations_count,
                ).add_condition(
                    "vehicle_plate LIKE ?",
                    vehicle_plate,
                ).add_condition(
                    "user_id = ?",
                    user_id,
                ).add_condition(
                    "violation_id >= ?",
                    min_id,
                ).add_condition(
                    "violation_id <= ?",
                    max_id,
                )

                await builder.execute(cursor.execute)
                rows = await cursor.fetchall()

        return [Violation.from_row(row) for row in rows]
