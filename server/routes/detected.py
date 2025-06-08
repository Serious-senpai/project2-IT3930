from __future__ import annotations

from datetime import datetime
from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BeforeValidator
from pyodbc import IntegrityError  # type: ignore

from ..config import DB_PAGINATION_QUERY
from ..models import Detected, User
from ..utils import snowflake_range


__all__ = ()
router = APIRouter(prefix="/detected", tags=["detected"])


@router.get(
    "/",
    summary="Query detected violations by cameras",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} detected violations from the database. The result is sorted by detected violation ID in descending order.",
    responses={
        403: {
            "description": "Missing `MANAGE_DETECTED` permission",
        },
    },
)
async def get_detected(
    user: Annotated[User, Depends(User.oauth2_decode)],
    detected_id: Annotated[Optional[int], Query(description="Filter by detected violation ID")] = None,
    # BeforeValidator(int): https://github.com/fastapi/fastapi/discussions/8966
    detected_category: Annotated[Optional[Literal[0, 1, 2]], Query(description="Filter by detected violation category"), BeforeValidator(int)] = None,
    detected_video_url: Annotated[
        Optional[str],
        Query(
            description="Filter by video URL [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    vehicle_plate: Annotated[
        Optional[str],
        Query(
            description="Filter by vehicle plate [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    user_id: Annotated[Optional[int], Query(description="Filter by violator ID")] = None,
    min_id: Annotated[Optional[int], Query(description="Minimum value for detected violation ID in the result set.")] = None,
    max_id: Annotated[Optional[int], Query(description="Maximum value for detected violation ID in the result set.")] = None,
    min_created_at: Optional[datetime] = None,
    max_created_at: Optional[datetime] = None,
) -> List[Detected]:
    if user.permission_obj.administrator or user.permission_obj.manage_detected:
        _min_id, _max_id = snowflake_range(min_created_at, max_created_at)
        min_id = max(min_id or _min_id, _min_id)
        max_id = min(max_id or _max_id, _max_id)

        return await Detected.query(
            detected_id=detected_id,
            detected_category=detected_category,
            detected_video_url=detected_video_url,
            vehicle_plate=vehicle_plate,
            user_id=user_id,
            min_id=min_id,
            max_id=max_id,
        )

    raise HTTPException(403, detail="Missing `MANAGE_DETECTED` permission")


@router.post(
    "/",
    summary="Add a new detected violation",
    description="Add a new detected violation to the database. Return the ID of the new detected violation.",
    responses={
        409: {
            "description": "Vehicle with this plate does not exist.",
        },
    },
)
async def add_detected(
    detected_category: Annotated[Literal[0, 1, 2], Query(description="The detected violation category"), BeforeValidator(int)],
    vehicle_plate: Annotated[str, Query(description="The vehicle plate", max_length=12)],
    detected_video_url: Annotated[str, Query(description="The URL to the video", max_length=2048)],
) -> int:
    try:
        return await Detected.create(
            detected_category=detected_category,
            vehicle_plate=vehicle_plate,
            detected_video_url=detected_video_url,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Vehicle with this plate does not exist.")


@router.delete(
    "/{detected_id}",
    summary="Remove a detected violation from the database",
    description="Remove a detected violation with the specified ID from the database.",
    status_code=204,
    response_model=None,
    responses={
        403: {
            "description": "Missing `MANAGE_DETECTED` permission.",
        },
        404: {
            "description": "Detected violation with this ID does not exist.",
        }
    },
)
async def delete_detected(
    user: Annotated[User, Depends(User.oauth2_decode)],
    detected_id: Annotated[int, Path(description="The detected violation ID")],
) -> None:
    if user.permission_obj.administrator or user.permission_obj.manage_detected:
        if await Detected.delete(detected_id=detected_id):
            return None

        raise HTTPException(404, detail="Detected violation with this ID does not exist.")

    raise HTTPException(403, detail="Missing `MANAGE_DETECTED` permission")
