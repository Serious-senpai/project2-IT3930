from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel
from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from .violations import Violation
from ..database import Database


__all__ = ("RefutationBody", "Refutation")


class RefutationBody(BaseModel):
    violation_id: int
    message: str

    async def create(self) -> Snowflake:
        async with Database.instance.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "EXECUTE create_refutation @ViolationId = ?, @Message = ?",
                    self.violation_id,
                    self.message,
                )

                id = await cursor.fetchval()
                return Snowflake(id=id)


class Refutation(Snowflake):
    message: str
    response: Optional[str]
    violation: Violation

    @classmethod
    def from_row(cls, row: Row) -> Refutation:
        return cls(
            id=row.r_id,
            message=row.r_message,
            response=row.r_response,
            violation=Violation.from_row(row),
        )

    @classmethod
    async def query(cls, *, id: Optional[int] = None) -> List[Refutation]:
        async with Database.instance.pool.acquire() as conn:
            async with conn.cursor() as cursor:

                if id is None:
                    await cursor.execute("SELECT * FROM refutations_view")
                else:
                    await cursor.execute("SELECT * FROM refutations_view WHERE r_id = ?", id)

                rows = await cursor.fetchall()
                return [cls.from_row(row) for row in rows]
