from typing import Annotated

from armasec import TokenPayload
from fastapi import APIRouter, Depends
from fastapi import status, Query
from pydantic import UUID4

from api.controllers import fetch_one_pin, fetch_many_pins
from api.permissions import Permissions
from api.security import guard
from api.schemas import Pin, FlatParams, Page

query_router = APIRouter(prefix="/queries", tags=["Pin query API"])


@query_router.get(
    "/{pin_id}",
    status_code=status.HTTP_200_OK,
    description="Endpoint used to fetch a pin by id",
    response_model_by_alias=False,  # This is horse-shit. See: https://github.com/fastapi/fastapi/issues/771
)
async def fetch_one_pin_route(
    pin_id: UUID4,
    token_payload: Annotated[TokenPayload, Depends(guard.lockdown(Permissions.READ_PINS))],
) -> Pin:
    """
    Fetch a single pin by id
    """
    owner_id: str = token_payload.sub
    pin: Pin = await fetch_one_pin(owner_id, pin_id)
    return pin


@query_router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Endpoint used to fetch a filtered set of pins",
    response_model_by_alias=False,  # This is horse-shit. See: https://github.com/fastapi/fastapi/issues/771
)
async def fetch_many_pins_route(
    query_params: Annotated[FlatParams, Query()],
    token_payload: Annotated[TokenPayload, Depends(guard.lockdown(Permissions.READ_PINS))],
) -> Page:
    owner_id: str = token_payload.sub
    # Calling with the flattened-query params is kinda goofy, but FastAPI doesn't support multiple
    # query params specified by pydantic models
    return await fetch_many_pins(owner_id, query_params, query_params)
