from __future__ import annotations

import asyncio
import itertools

from server.database import Database
from server.utils import hash_password


async def main() -> None:
    await Database.instance.prepare()

    async with Database.instance.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.executemany(
                "EXECUTE create_user @Fullname = ?, @Phone = ?, @HashedPassword = ?",
                [(f"Nguyễn Văn A {i:04}", f"0{i:04}12345", hash_password(f"test{i:04}")) for i in range(100)],
            )
            await cursor.execute("SELECT id FROM IT3930_Users ORDER BY phone")
            rows = await cursor.fetchall()
            user_ids = [row.id for row in rows]

            await cursor.executemany(
                "EXECUTE create_vehicle @Plate = ?, @UserId = ?",
                [(f"29T1-{i:05}", user_ids[i % 80]) for i in range(200)]
            )

            await cursor.executemany(
                "EXECUTE create_violation @CreatorId = ?, @Category = ?, @Plate = ?, @FineVnd = ?, @VideoUrl = ?",
                [(0, i % 3, f"29T1-{i:05}", (i + 1) * 1000, "https://files.catbox.moe/t32ctt.mp4") for i in range(100)]
            )

            await cursor.execute("SELECT id FROM IT3930_Violations ORDER BY fine_vnd")
            rows = await cursor.fetchall()
            violation_ids = [row.id for row in rows]

            await cursor.executemany(
                "EXECUTE create_refutation @ViolationId = ?, @UserId = ?, @Message = ?",
                itertools.chain(*[itertools.repeat((violation_ids[i], user_ids[i % 80], f"Refute {i}"), 2 * i) for i in range(50)]),
            )

            await cursor.executemany(
                "EXECUTE create_transaction @ViolationId = ?, @UserId = ?",
                [(violation_ids[i], user_ids[i % 80]) for i in range(100) if i % 2 == 0]
            )

    await Database.instance.close()


asyncio.run(main())
