from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel
from pyodbc import Row  # type: ignore

from .snowflake import Snowflake
from ..database import Database


__all__ = ("ViolationBody", "Violation")


class ViolationBody(BaseModel):
    category: Literal[0, 1, 2]
    plate: str
    fine_vnd: int
    video_url: str

    async def create(self) -> Violation:
        async with Database.instance.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "EXECUTE create_violation @Category = ?, @Plate = ?, @FineVnd = ?, @VideoUrl = ?",
                    self.category,
                    self.plate,
                    self.fine_vnd,
                    self.video_url,
                )

                id = await cursor.fetchval()
                return Violation(
                    id=id,
                    refutations_count=0,
                    transaction_id=None,
                    **self.model_dump(),
                )


class Violation(Snowflake, ViolationBody):
    refutations_count: int
    transaction_id: Optional[int]

    @classmethod
    def from_row(cls, row: Row) -> Violation:
        return cls(
            id=row.v_id,
            category=row.v_category,
            plate=row.v_plate,
            fine_vnd=row.v_fine_vnd,
            video_url=row.v_video_url,
            refutations_count=row.v_refutations_count,
            transaction_id=row.v_transaction_id,
        )

    @classmethod
    async def query(cls, *, id: Optional[int] = None) -> List[Violation]:
        async with Database.instance.pool.acquire() as conn:
            async with conn.cursor() as cursor:

                if id is None:
                    await cursor.execute("SELECT * FROM violations_view")
                else:
                    await cursor.execute("SELECT * FROM violations_view WHERE v_id = ?", id)

                rows = await cursor.fetchall()
                return [cls.from_row(row) for row in rows]
