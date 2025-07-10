import os

import jwt

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.dependencies import get_db

from src.users.schemas import UserModel

from src.auth.utils import hash_password, verify_password, create_access_token
from src.auth.config import SECRET_KEY, ALGORITHM
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

@pytest_asyncio.fixture
async def client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac
    app.dependency_overrides.clear()

def test_verify_password():
    password = 'foo'
    hashed_password = hash_password(password)

    assert password != hashed_password
    assert verify_password(password, hashed_password) == True
    assert verify_password('bar', hashed_password) == False

def test_create_access_token():
    fake_id = str(ObjectId())
    token = create_access_token({ 'sub': fake_id })
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload['sub'] == fake_id

@pytest.mark.asyncio
async def test_sign_up(client, test_db):
    data = {
        'name': 'Test User',
        'last_name': 'Test User',
        'email': 'test@example.com',
        'password': 'string',
    }

    response = await client.post("/sign-up", json=data)
    assert response.status_code == 201

    user = await test_db["users"].find_one({ "email": "test@example.com" })

    assert user is not None
    assert user["name"] == "Test User"
    assert user["last_name"] == "Test User"
    assert verify_password(data['password'], user['password'])

@pytest.mark.asyncio
async def test_sign_in(client, test_db, test_user):
    data = {
        'username': test_user['email'],
        'password': test_user['unhashed_password']
    }

    response = await client.post('/sign-in', data=data)
    assert response.status_code == 200

    token = response.json()
    user = await validate_token(token['access_token'], test_db['users'])

    assert user.id == str(test_user['_id'])

@pytest.mark.asyncio
async def test_sign_in_with_invalid_email(client, test_user):
    data = {
        'username': 'invalid@email.com',
        'password': test_user['unhashed_password']
    }

    response = await client.post('/sign-in', data=data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data['detail'] == 'Incorrect email or password'

@pytest.mark.asyncio
async def test_sign_in_with_invalid_password(client, test_user):
    data = {
        'username': test_user['email'],
        'password': 'invalid_password'
    }

    response = await client.post('/sign-in', data=data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data['detail'] == 'Incorrect email or password'
