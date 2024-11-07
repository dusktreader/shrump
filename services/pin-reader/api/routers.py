from typing import Annotated

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
    dependencies=[Depends(guard.lockdown(Permissions.READ_PINS))],
)
async def fetch_one_pin_route(pin_id: UUID4) -> Pin:
    pin: Pin = await fetch_one_pin(pin_id)
    return pin


@query_router.get(
    "",
    status_code=status.HTTP_200_OK,
    description="Endpoint used to fetch a filtered set of pins",
    response_model_by_alias=False,  # This is horse-shit. See: https://github.com/fastapi/fastapi/issues/771
    dependencies=[Depends(guard.lockdown(Permissions.READ_PINS))],
)
async def fetch_many_pins_route(
    query_params: Annotated[FlatParams, Query()],
) -> Page:
    # Calling with the flattened-query params is kinda goofy, but FastAPI doesn't support multiple
    # query params specified by pydantic models
    return await fetch_many_pins(query_params, query_params)
