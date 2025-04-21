from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models import Snowflake, Violation, ViolationBody


__all__ = ()
router = APIRouter(prefix="/violations")


@router.get("/")
async def get_violations(
    id: Annotated[Optional[int], Query(description="Filter by refutation ID")] = None,
    plate: Annotated[Optional[str], Query(description="Filter by plate number")] = None,
) -> List[Violation]:
    """Query all violations from the database"""
    return await Violation.query(id=id, plate=plate)


@router.post("/")
async def create_violation(body: ViolationBody) -> Violation:
    return await body.create()


@router.get(
    "/{violation_id}",
    responses={
        200: {"description": "The violation with the given ID"},
        404: {"description": "No violation was found"},
    },
)
async def get_violation(violation_id: int) -> Violation:
    """Query a violation by its ID"""
    violation = await Violation.query(id=violation_id)
    try:
        return violation[0]
    except IndexError:
        raise HTTPException(status_code=404, detail=f"No violation with ID {violation_id}")


@router.delete(
    "/{violation_id}",
    response_model=None,
    status_code=204,
    responses={
        204: {"description": "The operation completed successfully"},
        404: {"description": "No violation was found"},
    },
)
async def delete_violation(violation_id: int) -> None:
    """Delete a violation by its ID"""
    snowflake = Snowflake(id=violation_id)
    if not await Violation.delete(snowflake):
        raise HTTPException(status_code=404, detail=f"No violation with ID {violation_id}")
