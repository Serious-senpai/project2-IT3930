from __future__ import annotations

import atexit
import os
import secrets
import sys
from pathlib import Path
from typing import Any, ClassVar, Optional, TYPE_CHECKING

import aioodbc  # type: ignore

from .config import (
    EPOCH,
    MSSQL_DATABASE,
    MSSQL_HOST,
    MSSQL_PASSWORD,
    MSSQL_USER,
    ROOT,
)


__all__ = ("Database",)


class Database:
    """A database singleton that manages the connection pool."""

    instance: ClassVar[Database]
    __slots__ = (
        "__pool",
        "__prepared",
    )
    if TYPE_CHECKING:
        __pool: Optional[aioodbc.Pool]
        __prepared: bool

    def __init__(self) -> None:
        self.__pool = None
        self.__prepared = False

    @property
    def pool(self) -> aioodbc.Pool:
        """The underlying connection pool.

        In order to use this property, `.prepare()` must be called first.
        """
        if self.__pool is None:
            raise RuntimeError("Database is not connected. Did you call `.prepare()`?")

        return self.__pool

    async def prepare(self) -> None:
        """This function is a coroutine.

        Prepare the underlying connection pool. If the pool is already created, this function does nothing.
        """
        if self.__prepared:
            return

        self.__prepared = True

        self.__pool = pool = await aioodbc.create_pool(
            dsn=(
                "Driver={ODBC Driver 18 for SQL Server};"
                f"Server=tcp:{MSSQL_HOST},1433;"
                f"Database={MSSQL_DATABASE};Uid={MSSQL_USER};Pwd={MSSQL_PASSWORD};"
                "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
            ),
            minsize=10,
            maxsize=100,
            autocommit=True,
        )

        lock_file = ROOT / "database.lock"
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            print(f"Process {os.getpid()} will not initialize database (database.lock already exists).", file=sys.stderr)
            return
        finally:
            atexit.register(lock_file.unlink, missing_ok=True)

        print(f"Process {os.getpid()} is initializing database...", file=sys.stderr)

        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                async def execute(file: Path, *args: Any) -> None:
                    try:
                        with file.open("r", encoding="utf-8") as sql:
                            await cursor.execute(sql.read(), *args)

                    except Exception as e:
                        raise RuntimeError(f"Failed to execute {file}") from e

                scripts_dir = ROOT / "scripts"
                await execute(
                    scripts_dir / "schema.sql",
                    secrets.token_hex(32),
                    EPOCH,
                )

                await execute(scripts_dir / "procedures" / "generate_id.sql")
                for file in scripts_dir.glob("procedures/*.sql"):
                    if file.stem != "generate_id":
                        await execute(file)

                await execute(scripts_dir / "views" / "view_users.sql")
                await execute(scripts_dir / "views" / "view_vehicles.sql")
                await execute(scripts_dir / "views" / "view_violations.sql")
                await execute(scripts_dir / "views" / "view_refutations.sql")
                await execute(scripts_dir / "views" / "view_transactions.sql")

    async def close(self) -> None:
        if self.__pool is not None:
            self.__pool.close()
            await self.__pool.wait_closed()

        self.__prepared = False
        self.__pool = None


Database.instance = Database()
