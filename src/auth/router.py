from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .schemas import TokenModel
from .utils import verify_password, hash_password, create_access_token
from src.users.collection import user_collection
from src.users.schemas import UserModel
from src.users.dependencies import get_user_collection

auth_router = APIRouter(prefix='')

@auth_router.post(
    '/login', 
    response_model=TokenModel
)
async def login(login_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({ 'email': login_data.username })
    if user is None:
        raise HTTPException(
            status_code=401,
            detail='Incorrect email or password',
        )
    stored_user = UserModel(**user)
    if not verify_password(login_data.password, stored_user.password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect email or password',
        )
    access_token = create_access_token(
        data={ 'sub': stored_user.id }
    )
    return TokenModel(access_token=access_token, token_type='bearer')

@auth_router.post(
    '/sign-in',
    response_model=UserModel,
    status_code=201
)
async def sign_in(data: UserModel, user_collection = Depends(get_user_collection)):
    hashed_password = hash_password(data.password)
    user_data = data.model_dump(exclude=['id'], mode='json')
    user_data['password'] = hashed_password
    new_user = await user_collection.insert_one(user_data)
    created_user = await user_collection.find_one({ '_id': new_user.inserted_id })
    return created_user