from __future__ import annotations

from typing import List, Literal, Optional

from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from ..database import Database


__all__ = ("Violation",)


class Violation(Snowflake):
    category: Literal[0, 1, 2]
    plate: str
    fine_vnd: int
    refutations_count: int
    transaction_id: Optional[int]

    @classmethod
    def from_row(cls, row: Row) -> Violation:
        return cls(
            id=row.v_id,
            category=row.v_category,
            plate=row.v_plate,
            fine_vnd=row.v_fine_vnd,
            refutations_count=row.v_refutations_count,
            transaction_id=row.v_transaction_id,
        )

    @classmethod
    async def query(cls, *, id: Optional[int] = None) -> List[Violation]:
        db = Database.instance
        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:

                if id is None:
                    await cursor.execute("SELECT * FROM violations_view")
                else:
                    await cursor.execute("SELECT * FROM violations_view WHERE v_id = ?", id)

                rows = await cursor.fetchall()
                return [cls.from_row(row) for row in rows]
