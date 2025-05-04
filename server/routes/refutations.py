from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Query

from ..config import DB_PAGINATION_QUERY
from ..models import Refutation


__all__ = ()
router = APIRouter(prefix="/refutations")


@router.get(
    "/",
    summary="Query refutations",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} refutations from the database. The result is sorted by refutation ID in descending order.",
)
async def get_refutations(
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
    return await Refutation.query(
        refutation_id=refutation_id,
        refutation_message=refutation_message,
        refutation_response=refutation_response,
        violation_id=violation_id,
        vehicle_plate=vehicle_plate,
        user_id=user_id,
        min_id=min_id,
        max_id=max_id,
    )
