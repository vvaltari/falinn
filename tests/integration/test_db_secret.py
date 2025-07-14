import pytest
from bson import ObjectId

@pytest.mark.asyncio
async def test_get_secret(client, test_secret, override_authentication):
    secret_id = str(test_secret['_id'])
    response = await client.get(f'/secrets/{secret_id}')
    assert response.status_code == 200

    response_data = response.json()

    assert response_data['id'] == str(test_secret['_id'])
    assert response_data['name'] == test_secret['name']
    assert response_data['content']['email'] == test_secret['content']['email']

@pytest.mark.asyncio
async def test_get_secret_not_found(client, override_authentication):
    random_id = str(ObjectId())
    response = await client.get(f'/secrets/{random_id}')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_secret_invalid_id(client, override_authentication):
    invalid_id = 'invalid_id'
    response = await client.get(f'/secrets/{invalid_id}')
    assert response.status_code == 400