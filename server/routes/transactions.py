from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Query

from ..config import DB_PAGINATION_QUERY
from ..models import Transaction


__all__ = ()
router = APIRouter(prefix="/transactions")


@router.get(
    "/",
    summary="Query transactions",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} transactions from the database. The result is sorted by transaction ID in descending order.",
)
async def get_transactions(
    transaction_id: Annotated[Optional[int], Query(description="Filter by transaction ID")] = None,
    violation_id: Annotated[Optional[int], Query(description="Filter by violation ID")] = None,
    vehicle_plate: Annotated[
        Optional[str],
        Query(
            description="Filter by vehicle plate [pattern]"
            "(https://learn.microsoft.com/en-us/sql/t-sql/language-elements/like-transact-sql?view=sql-server-ver16#pattern).",
        ),
    ] = None,
    user_id: Annotated[Optional[int], Query(description="Filter by violator ID")] = None,
    payer_id: Annotated[Optional[int], Query(description="Filter by payer ID")] = None,
    min_id: Annotated[Optional[int], Query(description="Minimum value for transaction ID in the result set.")] = None,
    max_id: Annotated[Optional[int], Query(description="Maximum value for transaction ID in the result set.")] = None,
) -> List[Transaction]:
    return await Transaction.query(
        transaction_id=transaction_id,
        violation_id=violation_id,
        vehicle_plate=vehicle_plate,
        user_id=user_id,
        payer_id=payer_id,
        min_id=min_id,
        max_id=max_id,
    )
