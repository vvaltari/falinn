import os
import uuid
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from src.db import get_db
from src.auth.utils import hash_password, create_access_token
from src.auth.dependencies import validate_token
from src.users.schemas import UserModel
from src.main import app

@pytest.fixture
def db_client():
    DB_URI = os.getenv('DB_URI')
    client = AsyncIOMotorClient(DB_URI)
    yield client
    client.close()

@pytest.fixture
def test_db(db_client):
    TEST_DB_NAME = os.getenv('TEST_DB_NAME')
    db = db_client[TEST_DB_NAME]
    return db

# @pytest_asyncio.fixture(autouse=True)
# async def clear_db(test_db):
#     for collection_name in await test_db.list_collection_names():
#         await test_db[collection_name].delete_many({})

@pytest_asyncio.fixture
async def test_user(test_db):
    random_uuid = str(uuid.uuid4()) 

    user_data = {
        '_id': ObjectId(),
        'name': 'Test',
        'last_name': 'Test',
        'email': f'{random_uuid}@example.com',
        'unhashed_password': 'test_password'
    }

    user_data['password'] = hash_password(user_data['unhashed_password'])

    await test_db['users'].insert_one(user_data)
    return user_data

@pytest_asyncio.fixture
async def test_secret(test_db, test_user):
    secret_data = {
        '_id': ObjectId(),
        'name': 'string',
        'content': {
            'type': 'login',
            'email': 'test@example.com',
            'password': 'string',
            'sites': [ 
                'https://example.com/',
                'https://example.com/'
            ]
        },
        'description': 'string',
        'owner_id': test_user['_id']
    }

    await test_db['secrets'].insert_one(secret_data)
    return secret_data

@pytest_asyncio.fixture
async def test_token(test_user):
    token = create_access_token({ 'sub': str(test_user['_id']) })
    return token

@pytest_asyncio.fixture
async def override_authentication(test_user):
    app.dependency_overrides[validate_token] = lambda: UserModel(**test_user)
    yield
    del app.dependency_overrides[validate_token]

@pytest_asyncio.fixture
async def client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac
    app.dependency_overrides.clear()