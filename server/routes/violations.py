from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Depends, Query

from ..config import DB_PAGINATION_QUERY
from ..models import User, Violation


__all__ = ()
router = APIRouter(prefix="/violations")


@router.get(
    "/",
    summary="Query violations",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} violations from the database. The result is sorted by violation ID in descending order.",
)
async def get_violations(
    user: Annotated[User, Depends(User.oauth2_decode)],
    violation_id: Annotated[Optional[int], Query(description="Filter by violation ID")] = None,
    creator_id: Annotated[Optional[int], Query(description="Filter by creator ID")] = None,
    violation_category: Annotated[Optional[Literal[0, 1, 2]], Query(description="Filter by violation category")] = None,
    violation_fine_vnd: Annotated[Optional[int], Query(description="Filter by the fine amount in VND")] = None,
    violation_video_url: Annotated[
        Optional[str],
        Query(
            description="Filter by video URL [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    violation_refutations_count: Annotated[Optional[int], Query(description="Filter by the number of refutations")] = None,
    vehicle_plate: Annotated[
        Optional[str],
        Query(
            description="Filter by vehicle plate [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    user_id: Annotated[Optional[int], Query(description="Filter by violator ID")] = None,
    min_id: Annotated[Optional[int], Query(description="Minimum value for violation ID in the result set.")] = None,
    max_id: Annotated[Optional[int], Query(description="Maximum value for violation ID in the result set.")] = None,
) -> List[Violation]:
    if user.permission_obj.administrator or user.permission_obj.view_users:
        related_to = None
    else:
        related_to = user.id

    return await Violation.query(
        violation_id=violation_id,
        creator_id=creator_id,
        violation_category=violation_category,
        violation_fine_vnd=violation_fine_vnd,
        violation_video_url=violation_video_url,
        violation_refutations_count=violation_refutations_count,
        vehicle_plate=vehicle_plate,
        user_id=user_id,
        min_id=min_id,
        max_id=max_id,
        related_to=related_to,
    )
