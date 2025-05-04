from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import Field
from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from ..config import DB_PAGINATION_QUERY
from ..database import Database
from ..utils import SQLBuildHelper


__all__ = ("User",)


class User(Snowflake):
    """Represents a user"""

    fullname: Annotated[str, Field(description="The user's full name")]
    phone: Annotated[str, Field(description="The user's phone number")]
    permissions: Annotated[int, Field(description="The user's permissions flags")]
    vehicles_count: Annotated[int, Field(description="The number of vehicles the user has")]
    violations_count: Annotated[int, Field(description="The number of violations the user has")]

    @classmethod
    def from_row(cls, row: Row) -> User:
        return cls(
            id=row.user_id,
            fullname=row.user_fullname,
            phone=row.user_phone,
            permissions=row.user_permissions,
            vehicles_count=row.user_vehicles_count,
            violations_count=row.user_violations_count,
        )

    @staticmethod
    async def query(
        user_id: Optional[int] = None,
        user_fullname: Optional[str] = None,
        user_phone: Optional[str] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
    ) -> List[User]:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                builder = SQLBuildHelper(
                    "SELECT * FROM view_users",
                    f"ORDER BY user_id DESC OFFSET 0 ROWS FETCH NEXT {DB_PAGINATION_QUERY} ROWS ONLY",
                ).add_condition(
                    "user_id = ?",
                    user_id,
                ).add_condition(
                    "user_fullname LIKE ?",
                    user_fullname,
                ).add_condition(
                    "user_phone = ?",
                    user_phone,
                ).add_condition(
                    "user_id >= ?",
                    min_id,
                ).add_condition(
                    "user_id <= ?",
                    max_id,
                )

                await builder.execute(cursor.execute)
                rows = await cursor.fetchall()

        return [User.from_row(row) for row in rows]
