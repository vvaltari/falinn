import jwt
import os
from dotenv import load_dotenv
from typing import Annotated
from database import db
from bson import ObjectId
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from schemas import TokenModel, TokenDataModel, LoginModel, StoredUserModel

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

auth_router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
user_collection = db.get_collection('users')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(plain_password):
    return pwd_context.hash(plain_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({ 'exp': expire })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   
    return encoded_jwt

async def validate_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get('sub')
        if id is None:
            raise credentials_exception
        token_data = TokenDataModel(id=id)
    except InvalidTokenError:
        raise credentials_exception
    user = await user_collection.find_one({ '_id': ObjectId(token_data.id) })
    if user is None:
        raise credentials_exception
    return StoredUserModel(**user)

@auth_router.post(
    '/token', 
    response_model=TokenModel
)
async def login(login_data: LoginModel):
    user = await user_collection.find_one({ 'email': login_data.email })
    if user is None:
        raise HTTPException(
            status_code=401,
            detail='Incorrect email or password',
        )
    stored_user = StoredUserModel(**user)
    if not verify_password(login_data.password, stored_user.password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect email or password',
        )
    access_token = create_access_token(
        data={ 'sub': stored_user.id }
    )
    return TokenModel(access_token=access_token, token_type='bearer')