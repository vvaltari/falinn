import jwt
from bson import ObjectId
from src.auth.utils import hash_password, verify_password, create_access_token
from src.auth.config import SECRET_KEY, ALGORITHM

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
