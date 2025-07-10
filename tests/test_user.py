import os

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.dependencies import get_db

from src.users.schemas import UserModel

from src.auth.utils import hash_password, verify_password, create_access_token
from src.auth.dependencies import validate_token

from src.main import app



MONGO_URI = os.getenv('MONGO_URI')
TEST_DB_NAME = os.getenv('TEST_DB_NAME')

@pytest.fixture(scope='function')
def db_client():
    client = AsyncIOMotorClient(MONGO_URI)
    yield client
    client.close()

@pytest.fixture(scope='function')
def test_db(db_client):
    return db_client[TEST_DB_NAME]

@pytest_asyncio.fixture(autouse=True)
async def clear_db(test_db):
    for collection_name in await test_db.list_collection_names():
        await test_db[collection_name].delete_many({})

@pytest_asyncio.fixture
async def test_user(test_db):
    user_data = {
        '_id': ObjectId(),
        'name': 'Test',
        'last_name': 'Test',
        'email': 'test@example.com',
        'unhashed_password': 'test_password'
    }

    user_data['password'] = hash_password(user_data['unhashed_password'])

    await test_db['users'].insert_one(user_data)
    return user_data

@pytest_asyncio.fixture(autouse=True)
async def test_token(test_user):
    token = create_access_token({ 'sub': str(test_user['_id']) })
    return token

@pytest_asyncio.fixture
async def client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_me(client, test_token):
    headers = { 'Authorization': f'Bearer {test_token}'}

    response = await client.get('/users/me', headers=headers)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_me_invalid_token(client):
    headers = { 'Authorization': f'Bearer fake_token'}

    response = await client.get('/users/me', headers=headers)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_deleted_user_with_valid_token(client, test_db, test_user, test_token):
    await test_db['users'].delete_one({ '_id': test_user['_id'] })
    
    headers = { 'Authorization': f'Bearer {test_token}'}

    response = await client.get('/users/me', headers=headers)

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_user(client, test_db, test_user, test_token):
    data = {
        'name': 'Update test',
        'last_name': 'Update test',
        'email': 'updatetest@example.com'
    }

    headers = { 'Authorization': f'Bearer {test_token}'}

    response = await client.put('/users/', json=data, headers=headers)

    update_user = await test_db['users'].find_one({ '_id': test_user['_id'] })

    assert response.status_code == 200
    assert update_user['name'] == data['name']
    assert update_user['last_name'] == data['last_name']
    assert update_user['email'] == data['email']
    assert update_user['password'] == test_user['password']

@pytest.mark.asyncio
async def test_update_user_with_different_password(client, test_db, test_user, test_token):
    data = {
        'password': 'test_password',
    }

    headers = { 'Authorization': f'Bearer {test_token}'}

    response = await client.put('/users/', json=data, headers=headers)

    update_user = await test_db['users'].find_one({ '_id': test_user['_id'] })

    assert response.status_code == 200
    assert update_user['password'] != test_user['password']
    assert verify_password(data['password'], update_user['password']) == True

@pytest.mark.asyncio
async def test_update_user_empty_request(client, test_user, test_token):
    data = {}

    headers = { 'Authorization': f'Bearer {test_token}' }

    response = await client.put('/users/', json=data, headers=headers)

    user = response.json()

    assert response.status_code == 200
    assert user['id'] == str(test_user['_id'])
    assert user['name'] == test_user['name']
    assert user['last_name'] == test_user['last_name']
    assert user['email'] == test_user['email']

@pytest.mark.asyncio
async def test_update_user_not_found(client, test_token, test_user, test_db):
    app.dependency_overrides[validate_token] = lambda: UserModel(**test_user)
    await test_db['users'].delete_one({ '_id': test_user['_id'] })

    data = {
        'name': 'Update test',
        'last_name': 'Update test',
        'email': 'updatetest@example.com'
    }

    headers = { 'Authorization': f'Bearer {test_token}' }

    response = await client.put('/users/', json=data, headers=headers)

    app.dependency_overrides.clear()

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user_empty_request_user_not_found(client, test_token, test_user, test_db):
    app.dependency_overrides[validate_token] = lambda: UserModel(**test_user)
    await test_db['users'].delete_one({ '_id': test_user['_id'] })

    data = {}

    headers = { 'Authorization': f'Bearer {test_token}' }

    response = await client.put('/users/', json=data, headers=headers)

    app.dependency_overrides.clear()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(client, test_token, test_user, test_db):
    headers = { 'Authorization': f'Bearer {test_token}' }

    response = await client.delete('/users/', headers=headers)

    user = await test_db['users'].find_one({ '_id': test_user['_id'] })

    assert response.status_code == 204
    assert user == None

@pytest.mark.asyncio
async def test_delete_user_valid_token_deleted_user(client, test_token, test_user, test_db):
    app.dependency_overrides[validate_token] = lambda: UserModel(**test_user)
    await test_db['users'].delete_one({ '_id': test_user['_id'] })
    
    headers = { 'Authorization': f'Bearer {test_token}' }

    response = await client.delete('/users/', headers=headers)

    assert response.status_code == 404