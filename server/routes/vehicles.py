from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Query

from ..config import DB_PAGINATION_QUERY
from ..models import Vehicle


__all__ = ()
router = APIRouter(prefix="/vehicles")


@router.get(
    "/",
    summary="Query vehicles",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} vehicles from the database. The result is sorted by vehicle plate in ascending order.",
)
async def get_vehicles(
    vehicle_plate: Annotated[
        Optional[str],
        Query(
            description="Filter by vehicle plate [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    vehicle_violations_count: Annotated[Optional[int], Query(description="Filter by violations count")] = None,
    user_id: Annotated[Optional[int], Query(description="Filter by user ID")] = None,
    min_plate: Annotated[Optional[str], Query(description="Minimum value for vehicle plate in the result set (lexicography order).")] = None,
    max_plate: Annotated[Optional[str], Query(description="Maximum value for vehicle plate in the result set (lexicography order).")] = None,
) -> List[Vehicle]:
    return await Vehicle.query(
        vehicle_plate=vehicle_plate,
        vehicle_violations_count=vehicle_violations_count,
        user_id=user_id,
        min_plate=min_plate,
        max_plate=max_plate,
    )
