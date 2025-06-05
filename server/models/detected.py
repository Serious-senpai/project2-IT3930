from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from pydantic import Field
from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from .vehicles import Vehicle
from ..config import DB_PAGINATION_QUERY
from ..database import Database
from ..utils import SQLBuildHelper


__all__ = ("Detected",)


class Detected(Snowflake):
    """Represents a detected violation (but not yet confirmed by authorities)."""

    category: Annotated[Literal[0, 1, 2], Field(description="The detected violation category: 0 - speeding, 1 - red light, 2 - pavement")]
    video_url: Annotated[str, Field(description="The URL to the video")]
    vehicle: Annotated[Vehicle, Field(description="The vehicle associated with this detected violation")]

    @classmethod
    def from_row(cls, row: Row) -> Detected:
        return cls(
            id=row.detected_id,
            category=row.detected_category,
            video_url=row.detected_video_url,
            vehicle=Vehicle.from_row(row),
        )

    @classmethod
    @Database.retry()
    async def query(
        cls,
        *,
        detected_id: Optional[int] = None,
        detected_category: Optional[Literal[0, 1, 2]] = None,
        detected_video_url: Optional[str] = None,
        vehicle_plate: Optional[str] = None,
        user_id: Optional[int] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
    ) -> List[Detected]:
        pool = await Database.instance.pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                builder = SQLBuildHelper(
                    "SELECT * FROM view_detected",
                    ("ORDER BY detected_id DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY", (DB_PAGINATION_QUERY,)),
                ).add_condition(
                    "detected_id = ?",
                    detected_id,
                ).add_condition(
                    "detected_category = ?",
                    detected_category,
                ).add_condition(
                    "detected_video_url LIKE ?",
                    detected_video_url,
                ).add_condition(
                    "vehicle_plate LIKE ?",
                    vehicle_plate,
                ).add_condition(
                    "user_id = ?",
                    user_id,
                ).add_condition(
                    "detected_id >= ?",
                    min_id,
                ).add_condition(
                    "detected_id <= ?",
                    max_id,
                )

                await builder.execute(cursor.execute)
                rows = await cursor.fetchall()

        return [cls.from_row(row) for row in rows]

    @staticmethod
    @Database.retry()
    async def create(
        *,
        detected_category: Literal[0, 1, 2],
        vehicle_plate: str,
        detected_video_url: str,
    ) -> int:
        pool = await Database.instance.pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "EXECUTE create_detected @Category = ?, @Plate = ?, @VideoUrl = ?",
                    detected_category, vehicle_plate, detected_video_url,
                )
                id = await cursor.fetchval()
                return id

    @staticmethod
    @Database.retry()
    async def delete(
        *,
        detected_id: int
    ) -> bool:
        pool = await Database.instance.pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "EXECUTE delete_detected @Id = ?",
                    detected_id,
                )
                id = await cursor.fetchval()
                return id is not None
