from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pyodbc import IntegrityError  # type: ignore

from ..config import DB_PAGINATION_QUERY
from ..models import User, Vehicle


__all__ = ()
router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get(
    "/",
    summary="Query vehicles",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} vehicles from the database. The result is sorted by vehicle plate in ascending order.",
)
async def get_vehicles(
    user: Annotated[User, Depends(User.oauth2_decode)],
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
    if user.permission_obj.administrator or user.permission_obj.view_users:
        related_to = None
    else:
        related_to = user.id

    return await Vehicle.query(
        vehicle_plate=vehicle_plate,
        vehicle_violations_count=vehicle_violations_count,
        user_id=user_id,
        min_plate=min_plate,
        max_plate=max_plate,
        related_to=related_to,
    )


@router.post(
    "/",
    summary="Register a vehicle to the database",
    responses={
        403: {
            "description": "Missing `CREATE_VEHICLE` permission",
        },
        409: {
            "description": "Vehicle with this plate already exists.",
        },
    },
)
async def register_vehicle(
    user: Annotated[User, Depends(User.oauth2_decode)],
    vehicle_plate: Annotated[str, Query(description="The vehicle plate", max_length=12)],
    user_id: Annotated[
        Optional[int],
        Query(
            description="The user ID to register the vehicle to (you need `CREATE_VEHICLE` permission to register vehicles for other users)",
        ),
    ] = None,
) -> str:
    if not user.permission_obj.administrator and not user.permission_obj.create_vehicle:
        if user_id is not None and user_id != user.id:
            raise HTTPException(status_code=403, detail="Missing CREATE_VEHICLE permission")

    try:
        return await Vehicle.create(vehicle_plate=vehicle_plate, user_id=user.id)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Vehicle with this plate already exists.")
