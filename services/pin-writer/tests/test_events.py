import pytest
import uuid
from typing import Literal

from api.constants import EventKind
from api.events import EventService
from api.exceptions import EventServiceError
from api.schemas import Event


class DummyEvent(Event):
    kind: Literal[EventKind.TEST_EVENT] = EventKind.TEST_EVENT


async def test_get_context__success(mocker):
    mocked_nats = mocker.patch("api.events.nats")
    mocked_nats.connect = mocker.AsyncMock()
    mocked_nats.connect.return_value.jetstream = mocker.MagicMock()
    mocked_nats.connect.return_value.jetstream.return_value = mocker.AsyncMock()

    event_service = EventService()
    await event_service.get_context()
    mocked_nats.connect.assert_called_once_with(["nats://test-nats1:14222", "nats://test-nats2:14222"])
    mocked_nats.connect.return_value.jetstream.assert_called_once()
    mocked_nats.connect.return_value.jetstream.return_value.add_stream.assert_called_once_with(
        name="shrump",
        subjects=["events.pins"],
    )


async def test_get_context__raises_exception_if_connection_fails(mocker):
    mocked_nats = mocker.patch("api.events.nats")
    mocked_nats.connect = mocker.AsyncMock()
    mocked_nats.connect.side_effect = RuntimeError("Boom!")

    event_service = EventService()
    with pytest.raises(EventServiceError, match="Failed to connect to event bus"):
        await event_service.get_context()


async def test_send__success(mocker):
    event_service = EventService()

    mocked_js = mocker.patch.object(event_service, "get_context")
    test_uuid = uuid.uuid4()
    test_user = "The Dude"
    test_event = DummyEvent(pin_id=test_uuid, user_id=test_user)

    await event_service.send(test_event)
    mocked_js.assert_called_once()
    mocked_js.return_value.publish.assert_called_once_with(
        "events.pins", test_event.model_dump_json().encode()
    )
