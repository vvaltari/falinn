import jwt
from typing import Annotated
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from schemas.auth import TokenDataModel
from schemas.users import StoredUserModel
from auth import oauth2_scheme, SECRET_KEY, ALGORITHM
from database.collections import user_collection

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