from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Query

from ..config import DB_PAGINATION_QUERY
from ..models import User


__all__ = ()
router = APIRouter(prefix="/users")


@router.get(
    "/",
    summary="Query users",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} users from the database. The result is sorted by user ID in descending order.",
)
async def get_users(
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
) -> List[User]:
    return await User.query(
        user_id=user_id,
        user_fullname=user_fullname,
        user_phone=user_phone,
        min_id=min_id,
        max_id=max_id,
    )
