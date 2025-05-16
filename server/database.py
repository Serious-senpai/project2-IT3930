from __future__ import annotations

import asyncio
import atexit
import os
import secrets
import sys
from pathlib import Path
from typing import Any, Callable, ClassVar, Coroutine, Final, Optional, ParamSpec, TypeVar, TYPE_CHECKING

import aioodbc  # type: ignore
from pyodbc import OperationalError, ProgrammingError  # type: ignore

from .config import (
    EPOCH,
    MSSQL_DATABASE,
    MSSQL_HOST,
    MSSQL_PASSWORD,
    MSSQL_USER,
    ROOT,
)


__all__ = ("Database",)
_P = ParamSpec("_P")
_T = TypeVar("_T")
_CoroFunc = Callable[_P, Coroutine[Any, Any, _T]]


class Database:
    """A database singleton that manages the connection pool."""

    instance: ClassVar[Database]
    LOCK_FILE: ClassVar[Path] = ROOT / "database.lock"
    __slots__ = (
        "__pool",
        "__prepared",
        "__preparing",
        "__closing",
    )
    if TYPE_CHECKING:
        __pool: Optional[aioodbc.Pool]
        __prepared: Final[asyncio.Event]
        __preparing: bool
        __closing: bool

    def __init__(self) -> None:
        self.__pool = None
        self.__prepared = asyncio.Event()
        self.__preparing = False
        self.__closing = False

    async def pool(self) -> aioodbc.Pool:
        await self.prepare()
        await self.__prepared.wait()

        if self.__pool is None:
            raise RuntimeError("Connection pool is not initialized")

        return self.__pool

    async def prepare(self) -> None:
        """This function is a coroutine.

        Prepare the underlying connection pool. If the pool is already created, this function does nothing.
        """
        if self.__prepared.is_set() or self.__preparing:
            return

        self.__preparing = True
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

        try:
            fd = os.open(str(self.LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            print(f"Process {os.getpid()} will not initialize database (database.lock already exists).", file=sys.stderr)
            return
        finally:
            atexit.register(self.LOCK_FILE.unlink, missing_ok=True)

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

        self.__prepared.set()
        self.__preparing = False

    async def close(self) -> None:
        if self.__closing:
            return

        self.__closing = True
        try:
            pool = self.__pool
            self.__prepared.clear()
            self.__pool = None
            self.LOCK_FILE.unlink(missing_ok=True)

            if pool is not None:
                pool.close()
                await pool.wait_closed()

        finally:
            self.__closing = False

    @classmethod
    def retry(cls) -> Callable[[_CoroFunc[_P, _T]], _CoroFunc[_P, _T]]:
        def decorator(func: _CoroFunc[_P, _T]) -> _CoroFunc[_P, _T]:

            async def _impl(*args: _P.args, **kwargs: _P.kwargs) -> _T:
                try:
                    return await func(*args, **kwargs)

                except ProgrammingError as e:
                    # Handle connection failure
                    try:
                        original = e.__context__
                        if isinstance(original, OperationalError):
                            error_code = original.args[0]
                        else:
                            raise

                    except (AttributeError, IndexError):
                        pass

                    else:
                        if error_code == "08S01":
                            await cls.instance.close()
                            await cls.instance.prepare()

                            return await func(*args, **kwargs)

                    raise

            return _impl

        return decorator


Database.instance = Database()
