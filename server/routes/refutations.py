from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..models import Refutation


__all__ = ()
router = APIRouter(prefix="/refutations")


@router.get("/")
async def get_refutations() -> List[Refutation]:
    """Query all refutations from the database"""
    return await Refutation.query()


@router.get("/{refutation_id}")
async def get_refutation(refutation_id: int) -> Refutation:
    """Query a refutation by its ID"""
    refutation = await Refutation.query(id=refutation_id)
    try:
        return refutation[0]
    except IndexError:
        raise HTTPException(status_code=404, detail=f"No refutation with ID {refutation_id}")
