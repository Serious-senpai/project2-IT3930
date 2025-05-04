from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import BaseModel, Field
from pyodbc import Row  # type: ignore

from .users import User
from ..config import DB_PAGINATION_QUERY
from ..database import Database
from ..utils import SQLBuildHelper


__all__ = ("Vehicle",)


class Vehicle(BaseModel):
    """Represents a vehicle."""

    plate: Annotated[str, Field(description="The vehicle's plate number")]
    violations_count: Annotated[int, Field(description="The number of violations this vehicle has")]
    user: Annotated[User, Field(description="The user who owns this vehicle")]

    @classmethod
    def from_row(cls, row: Row) -> Vehicle:
        return cls(
            plate=row.vehicle_plate,
            violations_count=row.vehicle_violations_count,
            user=User.from_row(row),
        )

    @staticmethod
    async def query(
        vehicle_plate: Optional[str] = None,
        vehicle_violations_count: Optional[int] = None,
        user_id: Optional[int] = None,
        min_plate: Optional[str] = None,
        max_plate: Optional[str] = None,
    ) -> List[Vehicle]:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                builder = SQLBuildHelper(
                    "SELECT * FROM view_vehicles",
                    f"ORDER BY vehicle_plate ASC OFFSET 0 ROWS FETCH NEXT {DB_PAGINATION_QUERY} ROWS ONLY",
                ).add_condition(
                    "vehicle_plate LIKE ?",
                    vehicle_plate,
                ).add_condition(
                    "vehicle_violations_count = ?",
                    vehicle_violations_count,
                ).add_condition(
                    "user_id = ?",
                    user_id,
                ).add_condition(
                    "vehicle_plate >= ?",
                    min_plate,
                ).add_condition(
                    "vehicle_plate <= ?",
                    max_plate,
                )

                await builder.execute(cursor.execute)
                rows = await cursor.fetchall()

        return [Vehicle.from_row(row) for row in rows]
