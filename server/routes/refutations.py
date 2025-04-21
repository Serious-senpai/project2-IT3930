from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pyodbc import IntegrityError  # type: ignore

from ..models import Refutation, RefutationBody, Snowflake


__all__ = ()
router = APIRouter(prefix="/refutations")


@router.get("/")
async def get_refutations() -> List[Refutation]:
    """Query all refutations from the database"""
    return await Refutation.query()


@router.post("/")
async def create_refutation(body: RefutationBody) -> Snowflake:
    """Create a new refutation"""
    try:
        return await body.create()

    except IntegrityError:
        raise HTTPException(status_code=404, detail=f"No violation with ID {body.violation_id}")


@router.get("/{refutation_id}")
async def get_refutation(refutation_id: int) -> Refutation:
    """Query a refutation by its ID"""
    refutation = await Refutation.query(id=refutation_id)
    try:
        return refutation[0]
    except IndexError:
        raise HTTPException(status_code=404, detail=f"No refutation with ID {refutation_id}")
