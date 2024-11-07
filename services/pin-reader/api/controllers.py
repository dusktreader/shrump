from loguru import logger
from pydantic import UUID4

from api.schemas import Pin
from api.storage import get_pin_collection, paginate
from api.schemas import PinQueryParams, PaginationParams, Page


async def fetch_one_pin(pin_id: UUID4) -> Pin:
    pin_collection = get_pin_collection()
    pin_data = await pin_collection.find_one(dict(_id=pin_id))
    pin: Pin = Pin.model_validate(pin_data)
    return pin


async def fetch_many_pins(
    pin_params: PinQueryParams,
    page_params: PaginationParams,
) -> Page:
    pin_collection = get_pin_collection()
    query_dict = {}

    logger.debug(f"Searching for pins matching {pin_params=}")

    if "owner_id" in pin_params.model_fields_set:
        query_dict["owner_id"] = pin_params.owner_id

    if "created_after" in pin_params.model_fields_set:
        moment_subquery = query_dict.setdefault("moment_created", {})
        moment_subquery["$gte"] = pin_params.created_after

    if "created_before" in pin_params.model_fields_set:
        moment_subquery = query_dict.setdefault("moment_created", {})
        moment_subquery["$lte"] = pin_params.created_before

    if "updated_after" in pin_params.model_fields_set:
        moment_subquery = query_dict.setdefault("moment_last_updated", {})
        moment_subquery["$gte"] = pin_params.updated_after

    if "updated_before" in pin_params.model_fields_set:
        moment_subquery = query_dict.setdefault("moment_last_updated", {})
        moment_subquery["$lte"] = pin_params.updated_before

    results = pin_collection.find(query_dict)
    return await paginate(results, page_params)
