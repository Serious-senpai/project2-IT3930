from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Literal, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from pyodbc import IntegrityError  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm

from ..config import DB_PAGINATION_QUERY
from ..models import User
from ..utils import snowflake_range


__all__ = ()
router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    summary="Query users",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} users from the database. The result is sorted by user ID in descending order.",
)
async def get_users(
    user: Annotated[User, Depends(User.oauth2_decode)],
    user_id: Annotated[Optional[int], Query(description="Filter by user ID")] = None,
    user_fullname: Annotated[
        Optional[str],
        Query(
            description="Filter by full name [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    user_phone: Annotated[Optional[str], Query(description="Filter by phone number")] = None,
    min_id: Annotated[Optional[int], Query(description="Minimum value for user ID in the result set.")] = None,
    max_id: Annotated[Optional[int], Query(description="Maximum value for user ID in the result set.")] = None,
    min_created_at: Optional[datetime] = None,
    max_created_at: Optional[datetime] = None,
) -> List[User]:
    if user.permission_obj.administrator or user.permission_obj.view_users:
        related_to = None
    else:
        related_to = user.id

    _min_id, _max_id = snowflake_range(min_created_at, max_created_at)
    min_id = max(min_id or _min_id, _min_id)
    max_id = min(max_id or _max_id, _max_id)

    return await User.query(
        user_id=user_id,
        user_fullname=user_fullname,
        user_phone=user_phone,
        min_id=min_id,
        max_id=max_id,
        related_to=related_to,
    )


class __UserCreationPayload(BaseModel):
    """Payload for creating a new user"""

    fullname: Annotated[str, Field(description="The user's full name", max_length=255)]
    phone: Annotated[str, Field(description="The user's phone number", max_length=15)]
    password: Annotated[str, Field(description="The user's password")]


@router.post(
    "/",
    summary="Create a new user",
    description="Create a new user in the database. Return the ID of the new user.",
    responses={
        409: {
            "description": "User with this phone number already exists.",
        },
    },
)
async def create_user(payload: __UserCreationPayload) -> int:
    try:
        return await User.create(
            fullname=payload.fullname,
            phone=payload.phone,
            password=payload.password,
        )

    except IntegrityError:
        raise HTTPException(409, detail="User with this phone number already exists.")


class __LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


@router.post(
    "/login",
    summary="Login as an existing user",
    responses={
        401: {
            "description": "Invalid authentication credentials.",
        },
    }
)
async def login_user(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> __LoginResponse:
    id = await User.login(phone=form.username, password=form.password)
    if id is None:
        raise HTTPException(401, detail="Invalid authentication credentials.")

    data = {
        "id": id,
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=1),
    }

    return __LoginResponse(
        access_token=jwt.encode(data, await User.secret_key(), algorithm="HS256"),
        token_type="bearer",
    )


@router.get(
    "/@me",
    summary="Get the current user",
)
async def get_current_user(user: Annotated[User, Depends(User.oauth2_decode)]) -> User:
    return user
