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


__all__ = ("Transaction",)


class Transaction(Snowflake):
    """Represents a transaction."""

    violation: Annotated[Violation, Field(description="The violation associated with this transaction")]
    payer: Annotated[User, Field(description="The user who paid this transaction")]

    @classmethod
    def from_row(cls, row: Row) -> Transaction:
        return cls(
            id=row.transaction_id,
            violation=Violation.from_row(row),
            payer=User(
                id=row.payer_id,
                fullname=row.payer_fullname,
                phone=row.payer_phone,
                permissions=row.payer_permissions,
                vehicles_count=row.payer_vehicles_count,
                violations_count=row.payer_violations_count,
            ),
        )

    @classmethod
    @Database.retry()
    async def query(
        cls,
        *,
        transaction_id: Optional[int] = None,
        violation_id: Optional[int] = None,
        vehicle_plate: Optional[str] = None,
        user_id: Optional[int] = None,
        payer_id: Optional[int] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
        related_to: Optional[int] = None,
    ) -> List[Transaction]:
        pool = await Database.instance.pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                builder = SQLBuildHelper(
                    "SELECT * FROM view_transactions",
                    ("ORDER BY transaction_id DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY", (DB_PAGINATION_QUERY,)),
                ).add_condition(
                    "transaction_id = ?",
                    transaction_id,
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
                    "payer_id = ?",
                    payer_id,
                ).add_condition(
                    "transaction_id > ?",
                    min_id,
                ).add_condition(
                    "transaction_id < ?",
                    max_id,
                ).add_condition(
                    "creator_id = ? OR user_id = ? OR payer_id = ?",
                    related_to,
                    related_to,
                    related_to,
                )

                await builder.execute(cursor.execute)
                rows = await cursor.fetchall()

        return [cls.from_row(row) for row in rows]
