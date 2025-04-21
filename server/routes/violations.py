from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException

from ..models import Snowflake, Violation, ViolationBody


__all__ = ()
router = APIRouter(prefix="/violations")


@router.get("/")
async def get_violations(
    id: Annotated[Optional[int], "Filter by violation ID"] = None,
    plate: Annotated[Optional[str], "Filter by plate number"] = None,
) -> List[Violation]:
    """Query all violations from the database"""
    return await Violation.query(id=id, plate=plate)


@router.post("/")
async def create_violation(body: ViolationBody) -> Violation:
    return await body.create()


@router.get("/{violation_id}")
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
)
async def delete_violation(violation_id: int) -> None:
    """Delete a violation by its ID"""
    snowflake = Snowflake(id=violation_id)
    if not await Violation.delete(snowflake):
        raise HTTPException(status_code=404, detail=f"No violation with ID {violation_id}")
