import motor.motor_asyncio
from loguru import logger

from api.config import settings
from api.schemas import Page, PaginationParams, PinLot


# Make this injectable?
def get_pin_collection() -> motor.motor_asyncio.AsyncIOMotorCollection:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.DB_URL,
        uuidRepresentation="standard",
    )
    db = client.get_database(settings.DB_NAME)
    return db.get_collection("pins")


async def paginate(results: motor.motor_asyncio.AsyncIOMotorCursor, params: PaginationParams) -> Page:
    pin_data = await results.skip(params.page_size * params.page_number).limit(params.page_size).to_list()
    return Page(
        items=PinLot.model_validate(pin_data),
        page_size=params.page_size,
        page_number=params.page_number,
    )
