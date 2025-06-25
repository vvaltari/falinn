from fastapi import APIRouter, HTTPException
from database import user_collection
from schemas import LoginModel, TokenModel, StoredUserModel
from auth import verify_password, create_access_token

auth_router = APIRouter(prefix='/auth')

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