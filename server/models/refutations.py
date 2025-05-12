from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import Field
from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from .users import User
from .violations import Violation
from ..config import DB_PAGINATION_QUERY
from ..database import Database
from ..utils import SQLBuildHelper


__all__ = ("Refutation",)


class Refutation(Snowflake):
    """Represents a refutation."""

    message: Annotated[str, Field(description="The refutation message")]
    response: Annotated[Optional[str], Field(description="The response to the refutation")]
    author: Annotated[User, Field(description="The user who created the refutation")]
    violation: Annotated[Violation, Field(description="The violation associated with this refutation")]

    @classmethod
    def from_row(cls, row: Row) -> Refutation:
        return cls(
            id=row.refutation_id,
            message=row.refutation_message,
            response=row.refutation_response,
            author=User(
                id=row.author_id,
                fullname=row.author_fullname,
                phone=row.author_phone,
                permissions=row.author_permissions,
                vehicles_count=row.author_vehicles_count,
                violations_count=row.author_violations_count,
            ),
            violation=Violation.from_row(row),
        )

    @classmethod
    async def query(
        cls,
        *,
        refutation_id: Optional[int] = None,
        refutation_message: Optional[str] = None,
        refutation_response: Optional[str] = None,
        author_id: Optional[int] = None,
        violation_id: Optional[int] = None,
        vehicle_plate: Optional[str] = None,
        user_id: Optional[int] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
        related_to: Optional[int] = None,
    ) -> List[Refutation]:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                builder = SQLBuildHelper(
                    "SELECT * FROM view_refutations",
                    ("ORDER BY refutation_id DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY", (DB_PAGINATION_QUERY,)),
                ).add_condition(
                    "refutation_id = ?",
                    refutation_id,
                ).add_condition(
                    "refutation_message LIKE ?",
                    refutation_message,
                ).add_condition(
                    "refutation_response LIKE ?",
                    refutation_response,
                ).add_condition(
                    "author_id = ?",
                    author_id,
                ).add_condition(
                    "violation_id = ?",
                    violation_id,
                ).add_condition(
                    "vehicle_plate LIKE ?",
                    vehicle_plate,
                ).add_condition(
                    "user_id = ?",
                    user_id,
                ).add_condition(
                    "refutation_id >= ?",
                    min_id,
                ).add_condition(
                    "refutation_id <= ?",
                    max_id,
                ).add_condition(
                    "author_id = ? OR creator_id = ? OR user_id = ?",
                    related_to,
                    related_to,
                    related_to,
                )

                await builder.execute(cursor.execute)
                rows = await cursor.fetchall()

        return [cls.from_row(row) for row in rows]

    @staticmethod
    async def create(
        *,
        violation_id: int,
        user_id: int,
        message: str,
    ) -> int:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "EXECUTE create_refutation @ViolationId = ?, @UserId = ?, @Message = ?",
                    violation_id, user_id, message,
                )
                id = await cursor.fetchval()
                return id
