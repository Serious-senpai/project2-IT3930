from __future__ import annotations

import asyncio
import itertools

from server.database import Database


async def main() -> None:
    await Database.instance.prepare()

    async with Database.instance.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.executemany(
                "EXECUTE create_violation @Category = ?, @Plate = ?, @Fine_vnd = ?",
                [(i % 3, f"29T1-{i:05}", i * 1000) for i in range(100)]
            )

            await cursor.execute("SELECT id FROM Violations")
            rows = await cursor.fetchall()
            ids = [row.id for row in rows]

            await cursor.executemany(
                "EXECUTE create_refutation @ViolationId = ?, @Message = ?",
                itertools.chain(*[itertools.repeat((ids[i], f"Refute {i}"), 2 * i) for i in range(50)]),
            )

            await cursor.executemany(
                "EXECUTE create_transaction @ViolationId = ?",
                [(ids[i],) for i in range(100) if i % 2 == 0]
            )

    await Database.instance.close()


asyncio.run(main())
