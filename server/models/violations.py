from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from pydantic import Field
from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from .users import User
from .vehicles import Vehicle
from ..config import DB_PAGINATION_QUERY
from ..database import Database
from ..utils import SQLBuildHelper


__all__ = ("Violation",)


class Violation(Snowflake):
    """Represents a violation."""

    creator: Annotated[User, Field(description="The user who submitted this violation (this is not the violator)")]
    category: Annotated[Literal[0, 1, 2], Field(description="The violation category: 0 - speeding, 1 - red light, 2 - pavement")]
    fine_vnd: Annotated[int, Field(description="The fine amount in VND")]
    video_url: Annotated[str, Field(description="The URL to the video")]
    refutations_count: Annotated[int, Field(description="The number of refutations of this violation")]
    vehicle: Annotated[Vehicle, Field(description="The vehicle associated with this violation")]

    @classmethod
    def from_row(cls, row: Row) -> Violation:
        return cls(
            id=row.violation_id,
            creator=User(
                id=row.creator_id,
                fullname=row.creator_fullname,
                phone=row.creator_phone,
                permissions=row.creator_permissions,
                vehicles_count=row.creator_vehicles_count,
                violations_count=row.creator_violations_count,
            ),
            category=row.violation_category,
            fine_vnd=row.violation_fine_vnd,
            video_url=row.violation_video_url,
            refutations_count=row.violation_refutations_count,
            vehicle=Vehicle.from_row(row),
        )

    @classmethod
    @Database.retry()
    async def query(
        cls,
        *,
        violation_id: Optional[int] = None,
        creator_id: Optional[int] = None,
        violation_category: Optional[Literal[0, 1, 2]] = None,
        violation_fine_vnd: Optional[int] = None,
        violation_video_url: Optional[str] = None,
        violation_refutations_count: Optional[int] = None,
        vehicle_plate: Optional[str] = None,
        user_id: Optional[int] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
        related_to: Optional[int] = None,
    ) -> List[Violation]:
        pool = await Database.instance.pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                builder = SQLBuildHelper(
                    "SELECT * FROM view_violations",
                    ("ORDER BY violation_id DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY", (DB_PAGINATION_QUERY,)),
                ).add_condition(
                    "violation_id = ?",
                    violation_id,
                ).add_condition(
                    "creator_id = ?",
                    creator_id,
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
                ).add_condition(
                    "creator_id = ? OR user_id = ?",
                    related_to,
                    related_to,
                )

                await builder.execute(cursor.execute)
                rows = await cursor.fetchall()

        return [cls.from_row(row) for row in rows]

    @staticmethod
    @Database.retry()
    async def create(
        *,
        creator_id: int,
        violation_category: Literal[0, 1, 2],
        vehicle_plate: str,
        violation_fine_vnd: int,
        violation_video_url: str,
    ) -> int:
        pool = await Database.instance.pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "EXECUTE create_violation @CreatorId = ?, @Category = ?, @Plate = ?, @FineVND = ?, @VideoUrl = ?",
                    creator_id, violation_category, vehicle_plate, violation_fine_vnd, violation_video_url,
                )
                id = await cursor.fetchval()
                return id
