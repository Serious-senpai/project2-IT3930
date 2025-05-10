from __future__ import annotations

from typing import Annotated, List, Optional

import jwt
from fastapi import Depends, HTTPException
from pydantic import Field
from pyodbc import Row  # type: ignore
from fastapi.security import OAuth2PasswordBearer

from .snowflake import Snowflake
from ..config import DB_PAGINATION_QUERY
from ..database import Database
from ..utils import SQLBuildHelper, check_password, hash_password


__all__ = ("User",)


OAUTH2_SCHEME = OAuth2PasswordBearer("/users/login")


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

    @classmethod
    async def oauth2_decode(cls, token: Annotated[str, Depends(OAUTH2_SCHEME)]) -> User:
        error = HTTPException(status_code=401, detail="Invalid authentication credentials")
        try:
            payload = jwt.decode(
                token,
                await cls.secret_key(),
                algorithms=["HS256"],
            )
        except jwt.PyJWTError:
            raise error

        try:
            user_id = payload["id"]
        except KeyError:
            raise error

        users = await cls.query(user_id=user_id)
        assert len(users) < 2
        try:
            return users[0]
        except IndexError:
            raise error

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
                    ("ORDER BY user_id DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY", (DB_PAGINATION_QUERY,)),
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

    @staticmethod
    async def create(*, fullname: str, phone: str, password: str) -> int:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "EXECUTE create_user @Fullname = ?, @Phone = ?, @HashedPassword = ?",
                    fullname, phone, hash_password(password)
                )
                id = await cursor.fetchval()
                return id

    @classmethod
    async def login(cls, *, phone: str, password: str) -> Optional[int]:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT id, hashed_password FROM IT3930_Users WHERE phone = ?", phone)
                row = await cursor.fetchone()
                if row is None:
                    return None

                if check_password(password, hashed=row.hashed_password):
                    return row.id

        return None

    @staticmethod
    async def secret_key() -> str:
        async with Database.instance.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT value FROM IT3930_Config WHERE name = ?", "session_secret_key")
                return await cursor.fetchval()
