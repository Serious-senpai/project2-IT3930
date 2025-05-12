from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from pyodbc import IntegrityError  # type: ignore

from ..config import DB_PAGINATION_QUERY
from ..models import Refutation, User, Violation


__all__ = ()
router = APIRouter(prefix="/refutations", tags=["refutations"])


@router.get(
    "/",
    summary="Query refutations",
    description=f"Query a maximum of {DB_PAGINATION_QUERY} refutations from the database. The result is sorted by refutation ID in descending order.",
)
async def get_refutations(
    user: Annotated[User, Depends(User.oauth2_decode)],
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
    author_id: Annotated[Optional[int], Query(description="Filter by author ID")] = None,
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
    if user.permission_obj.administrator or user.permission_obj.view_users:
        related_to = None
    else:
        related_to = user.id

    return await Refutation.query(
        refutation_id=refutation_id,
        refutation_message=refutation_message,
        refutation_response=refutation_response,
        author_id=author_id,
        violation_id=violation_id,
        vehicle_plate=vehicle_plate,
        user_id=user_id,
        min_id=min_id,
        max_id=max_id,
        related_to=related_to,
    )


class __RefutationCreationPayload(BaseModel):
    """Payload for creating a new refutation."""

    violation_id: Annotated[
        int,
        Field(
            description="The violation ID to refute (you need `CREATE_REFUTATION` permission to refute someone else's violation).",
        ),
    ]
    message: Annotated[str, Field(description="The refutation message.", max_length=4096)]


@router.post(
    "/",
    summary="Create a new refutation",
    description="Create a new refutation in the database. Return the refutation ID.",
    responses={
        403: {
            "description": "Missing `CREATE_REFUTATION` permission",
        },
        409: {
            "description": "The provided violation ID does not exist.",
        },
    },
)
async def create_refutation(
    user: Annotated[User, Depends(User.oauth2_decode)],
    payload: __RefutationCreationPayload,
) -> int:
    conflict = HTTPException(status_code=409, detail="The provided violation ID does not exist.")
    if not user.permission_obj.administrator and not user.permission_obj.create_refutation:
        # Check that `user` is the same as `violation.vehicle.user`
        violations = await Violation.query(violation_id=payload.violation_id)
        if len(violations) != 1:
            raise conflict

        violation = violations[0]
        if violation.vehicle.user != user:
            raise HTTPException(status_code=403, detail="Missing `CREATE_REFUTATION` permission")

    try:
        return await Refutation.create(
            violation_id=payload.violation_id,
            user_id=user.id,
            message=payload.message,
        )
    except IntegrityError:
        raise conflict


class __RefutationResponsePayload(BaseModel):
    """Payload for responding to a refutation."""

    refutation_id: Annotated[int, Field(description="The refutation ID to respond to.")]
    response: Annotated[str, Field(description="The response message.", max_length=4096)]


@router.post(
    "/response",
    summary="Respond to a refutation",
    description="Respond to a refutation in the database.",
    status_code=204,
    response_model=None,
    responses={
        403: {
            "description": "Missing `RESPOND_REFUTATION` permission",
        },
        409: {
            "description": "The provided refutation ID does not exist.",
        },
    },
)
async def refutation_response(
    user: Annotated[User, Depends(User.oauth2_decode)],
    payload: __RefutationResponsePayload,
) -> None:
    if not user.permission_obj.administrator and not user.permission_obj.respond_refutation:
        raise HTTPException(status_code=403, detail="Missing `RESPOND_REFUTATION` permission")

    id = await Refutation.respond(refutation_id=payload.refutation_id, response=payload.response)
    if id is None:
        raise HTTPException(status_code=409, detail="The provided refutation ID does not exist.")

    return None
