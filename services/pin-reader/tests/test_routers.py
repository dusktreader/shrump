import uuid

from fastapi import status

from api.constants import DEFAULT_PAGE_SIZE
from api.permissions import Permissions
from api.schemas import Coords, FlatParams, Pin, PinLot, Page


async def test_query_pin_get_one(client, mocker, inject_security_header):
    test_uuid = uuid.uuid4()
    test_pin = Pin(
        id=test_uuid,
        owner_id="The Dude",
        coords=Coords(
            latitude=13,
            longitude=21,
        ),
        moment_created="2024-11-05 20:26:00",
        moment_last_updated="2024-11-05 20:26:00",
    )
    mock_fetch = mocker.patch("api.routers.fetch_one_pin", return_value=test_pin)
    inject_security_header(permissions=[Permissions.READ_PINS])
    response = await client.get(f"/queries/{test_uuid}")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data == test_pin.model_dump(mode="json")
    mock_fetch.assert_called_once_with(test_uuid)


async def test_query_pin_get_many(client, mocker, inject_security_header):
    test_uuid1 = uuid.uuid4()
    test_uuid2 = uuid.uuid4()
    test_pins = PinLot(
        [
            Pin(
                id=test_uuid1,
                owner_id="The Dude",
                coords=Coords(
                    latitude=13,
                    longitude=21,
                ),
                moment_created="2024-11-05 20:26:00",
                moment_last_updated="2024-11-05 20:26:00",
            ),
            Pin(
                id=test_uuid2,
                owner_id="walter",
                coords=Coords(
                    latitude=31,
                    longitude=12,
                ),
                moment_created="2024-11-05 21:34:00",
                moment_last_updated="2024-11-05 21:34:00",
            ),
        ],
    )
    test_page = Page(
        items=test_pins,
        page_size=DEFAULT_PAGE_SIZE,
        page_number=0,
    )
    mock_fetch = mocker.patch("api.routers.fetch_many_pins", return_value=test_page)
    inject_security_header(permissions=[Permissions.READ_PINS])
    response = await client.get(f"/queries")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data == test_page.model_dump(mode="json")

    test_params = FlatParams()
    mock_fetch.assert_called_once_with(test_params, test_params)
