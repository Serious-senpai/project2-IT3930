from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query

from ..config import DB_PAGINATION_QUERY
from ..models import Refutation, User


__all__ = ()
router = APIRouter(prefix="/refutations")


@router.get(
    "/",
    summary="Query refutations",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} refutations from the database. The result is sorted by refutation ID in descending order.",
)
async def get_refutations(
    user: Annotated[User, Depends(User.oauth2_decode)],
    refutation_id: Annotated[Optional[int], Query(description="Filter by refutation ID")] = None,
    refutation_message: Annotated[
        Optional[str],
        Query(
            description="Filter by refutation message [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    refutation_response: Annotated[
        Optional[str],
        Query(
            description="Filter by refutation response [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    author_id: Annotated[Optional[int], Query(description="Filter by author ID")] = None,
    violation_id: Annotated[Optional[int], Query(description="Filter by violation ID")] = None,
    vehicle_plate: Annotated[
        Optional[str],
        Query(
            description="Filter by vehicle plate [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    user_id: Annotated[Optional[int], Query(description="Filter by violator ID")] = None,
    min_id: Annotated[Optional[int], Query(description="Minimum value for refutation ID in the result set.")] = None,
    max_id: Annotated[Optional[int], Query(description="Maximum value for refutation ID in the result set.")] = None,
) -> List[Refutation]:
    if not user.permission_obj.administrator and not user.permission_obj.view_users:
        if author_id is None:
            author_id = user.id
        elif author_id != user.id:
            return []

        if user_id is None:
            user_id = user.id
        elif user_id != user.id:
            return []

    return await Refutation.query(
        refutation_id=refutation_id,
        refutation_message=refutation_message,
        refutation_response=refutation_response,
        author_id=author_id,
        violation_id=violation_id,
        vehicle_plate=vehicle_plate,
        user_id=user_id,
        min_id=min_id,
        max_id=max_id,
    )
