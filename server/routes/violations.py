from __future__ import annotations

from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BeforeValidator
from pyodbc import IntegrityError  # type: ignore

from ..config import DB_PAGINATION_QUERY
from ..models import User, Violation


__all__ = ()
router = APIRouter(prefix="/violations", tags=["violations"])


@router.get(
    "/",
    summary="Query violations",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} violations from the database. The result is sorted by violation ID in descending order.",
)
async def get_violations(
    user: Annotated[User, Depends(User.oauth2_decode)],
    violation_id: Annotated[Optional[int], Query(description="Filter by violation ID")] = None,
    creator_id: Annotated[Optional[int], Query(description="Filter by creator ID")] = None,
    # BeforeValidator(int): https://github.com/fastapi/fastapi/discussions/8966
    violation_category: Annotated[Optional[Literal[0, 1, 2]], Query(description="Filter by violation category"), BeforeValidator(int)] = None,
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


@router.post(
    "/",
    summary="Add a new violation",
    description="Add a new violation to the database. Return the ID of the new violation.",
    responses={
        403: {
            "description": "Missing `CREATE_VIOLATION` permission",
        },
        409: {
            "description": "Vehicle with this plate does not exist.",
        },
    },
)
async def add_violation(
    user: Annotated[User, Depends(User.oauth2_decode)],
    violation_category: Annotated[Literal[0, 1, 2], Query(description="The violation category"), BeforeValidator(int)],
    vehicle_plate: Annotated[str, Query(description="The vehicle plate", max_length=12)],
    violation_fine_vnd: Annotated[int, Query(description="The fine amount in VND")],
    violation_video_url: Annotated[str, Query(description="The URL to the video", max_length=2048)],
) -> int:
    if not user.permission_obj.administrator and not user.permission_obj.create_violation:
        raise HTTPException(status_code=403, detail="Missing CREATE_VIOLATION permission")

    try:
        return await Violation.create(
            creator_id=user.id,
            violation_category=violation_category,
            vehicle_plate=vehicle_plate,
            violation_fine_vnd=violation_fine_vnd,
            violation_video_url=violation_video_url,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Vehicle with this plate does not exist.")


@router.get(
    "/{plate}",
    summary="Query violations by vehicle plate",
    description=(
        f"Query a maximum of {DB_PAGINATION_QUERY} violations from the database. The result is sorted by violation ID in descending order.\n\n"
        "This endpoint does not require authorization."
    ),
)
async def get_violations_by_plate(
    plate: Annotated[
        str,
        Path(
            description="Filter by vehicle plate [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ],
) -> List[Violation]:
    return await Violation.query(vehicle_plate=plate)
