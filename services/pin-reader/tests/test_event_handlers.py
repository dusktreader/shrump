import uuid
from api.event_handlers import create_pin
from plummet import frozen_time, momentize

from api.schemas import Coords, PinDropped


async def test_create_pin__success(mocker):
    mock_collection = mocker.patch("api.event_handlers.get_pin_collection")
    mock_collection.return_value.count_documents = mocker.AsyncMock(return_value=0)
    mock_collection.return_value.insert_one = mocker.AsyncMock()

    test_id = uuid.uuid4()
    with frozen_time("2024-11-05 22:00:01"):
        test_drop = PinDropped(
            pin_id=test_id,
            coords=Coords(
                latitude=13,
                longitude=21,
            ),
            user_id="The Dude",
        )
    await create_pin(test_drop)

    mock_collection.assert_called_once()
    mock_collection.return_value.count_documents.assert_called_once_with(dict(_id=test_id))
    mock_collection.return_value.insert_one.assert_called_once_with(
        dict(
            _id=test_id,
            owner_id="The Dude",
            coords=dict(
                latitude=13,
                longitude=21,
            ),
            moment_created=momentize("2024-11-05 22:00:01"),
            moment_last_updated=momentize("2024-11-05 22:00:01"),
        )
    )


async def test_create_pin__does_not_create_if_pin_already_exists(mocker, caplog):
    mock_collection = mocker.patch("api.event_handlers.get_pin_collection")
    mock_collection.return_value.count_documents = mocker.AsyncMock(return_value=1)
    mock_collection.return_value.insert_one = mocker.AsyncMock()

    test_id = uuid.uuid4()
    with frozen_time("2024-11-05 22:00:01"):
        test_drop = PinDropped(
            pin_id=test_id,
            coords=Coords(
                latitude=13,
                longitude=21,
            ),
            user_id="The Dude",
        )
    await create_pin(test_drop)

    mock_collection.assert_called_once()
    mock_collection.return_value.count_documents.assert_called_once_with(dict(_id=test_id))
    mock_collection.return_value.insert_one.assert_not_called()
