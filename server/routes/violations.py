from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..models import Violation


__all__ = ()
router = APIRouter(prefix="/violations")


@router.get("/")
async def get_violations() -> List[Violation]:
    """Query all violations from the database"""
    return await Violation.query()


@router.get("/{violation_id}")
async def get_violation(violation_id: int) -> Violation:
    """Query a violation by its ID"""
    violation = await Violation.query(id=violation_id)
    try:
        return violation[0]
    except IndexError:
        raise HTTPException(status_code=404, detail=f"No violation with ID {violation_id}")
