import uuid

from fastapi import status

from api.permissions import Permissions


async def test_drop_pin_post(client, mocker, inject_security_header):
    test_uuid = uuid.uuid4()
    mocker.patch("api.routers.drop_pin", return_value=test_uuid)
    inject_security_header(permissions=[Permissions.WRITE_PINS])
    response = await client.post(
        "/commands/drop-pin",
        json=dict(
            latitude=13,
            longitude=21,
        ),
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data == str(test_uuid)
