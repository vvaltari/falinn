from fastapi import APIRouter, HTTPException, Depends
from database.collections import user_collection
from schemas.auth import TokenModel
from schemas.users import StoredUserModel
from auth.auth import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix='')

@auth_router.post(
    '/token', 
    response_model=TokenModel
)
async def login(login_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({ 'email': login_data.username })
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