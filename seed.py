from __future__ import annotations

import asyncio
import itertools
import random
from typing import Dict, List

from server.database import Database
from server.utils import hash_password


BATCH_SIZE = 32


async def main() -> None:
    pool = await Database.instance.pool()
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            cursor._impl.fast_executemany = True

            for indices in itertools.batched(range(1000), BATCH_SIZE):
                await cursor.executemany(
                    "EXECUTE create_user @Fullname = ?, @Phone = ?, @HashedPassword = ?",
                    [(f"Nguyễn Văn A {i}", f"09{i:08}", hash_password(f"test{i:08}")) for i in indices],
                )

            await cursor.execute("SELECT id FROM IT3930_Users ORDER BY id")
            rows = await cursor.fetchall()
            user_ids: List[int] = [row.id for row in rows]

            owners = {f"29T1-{i:05}": random.choice(user_ids) for i in range(2000)}
            for vh in itertools.batched(owners.items(), BATCH_SIZE):
                await cursor.executemany("EXECUTE create_vehicle @Plate = ?, @UserId = ?", vh)

            for plates in itertools.batched(owners.keys(), BATCH_SIZE):
                await cursor.executemany(
                    "EXECUTE create_violation @CreatorId = ?, @Category = ?, @Plate = ?, @FineVnd = ?, @VideoUrl = ?",
                    [(0, random.randint(0, 2), plate, random.randint(100, 6000) * 1000, "https://files.catbox.moe/t32ctt.mp4") for plate in plates],
                )

            await cursor.execute("SELECT id, plate FROM IT3930_Violations ORDER BY id")
            rows = await cursor.fetchall()
            violation_ids: Dict[int, str] = {row.id: row.plate for row in rows}

            for id, plate in violation_ids.items():
                vl = [(id, owners[plate], f"Khiếu nại {i} cho xe {plate}") for i in range(random.randint(0, 4))]
                if vl:
                    await cursor.executemany("EXECUTE create_refutation @ViolationId = ?, @UserId = ?, @Message = ?", vl)

            transaction_values = [(id, owners[plate]) for id, plate in violation_ids.items() if random.random() < 0.3]
            for t in itertools.batched(transaction_values, BATCH_SIZE):
                await cursor.executemany("EXECUTE create_transaction @ViolationId = ?, @UserId = ?", t)

    await Database.instance.close()


asyncio.run(main())
