from bson import ObjectId
import pytest
from tests.utils import make_user_payload, make_sign_in_payload
from src.auth.utils import verify_password
from src.auth.dependencies import validate_token

@pytest.mark.asyncio
async def test_sign_up(client, test_db):
    data = make_user_payload()

    response = await client.post("/sign-up", json=data)
    assert response.status_code == 201

    response_data = response.json()

    user = await test_db["users"].find_one({ "_id": ObjectId(response_data['_id']) })

    assert user is not None
    assert user["name"] == "Test User"
    assert user["last_name"] == "Test User"
    assert verify_password(data['password'], user['password'])

@pytest.mark.asyncio
async def test_sign_in(client, test_db, test_user):
    data = make_sign_in_payload(username=test_user['email'], password=test_user['unhashed_password'])

    response = await client.post('/sign-in', data=data)
    assert response.status_code == 200

    token = response.json()
    user = await validate_token(token['access_token'], test_db['users'])

    assert user.id == str(test_user['_id'])

@pytest.mark.asyncio
async def test_sign_in_with_invalid_email(client, test_user):
    data = make_sign_in_payload(password=test_user['unhashed_password'])

    response = await client.post('/sign-in', data=data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data['detail'] == 'Incorrect email or password'

@pytest.mark.asyncio
async def test_sign_in_with_invalid_password(client, test_user):
    data = make_sign_in_payload(username=test_user['email'])

    response = await client.post('/sign-in', data=data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data['detail'] == 'Incorrect email or password'
