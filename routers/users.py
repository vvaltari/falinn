from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from pymongo import ReturnDocument
from database.collections import user_collection
from schemas.users import UserModel, UpdateUserModel
from auth.auth import hash_password
from auth.dependencies import validate_token

users_router = APIRouter(prefix='/users')

@users_router.get(
    '/me',
    response_description='List a user',
    response_model=UserModel,
    response_model_by_alias=False
)
async def get_user(user: UserModel = Depends(validate_token)):
    return user

@users_router.put(
    '/',
    response_description='Update a user',
    response_model=UserModel,
    response_model_by_alias=False
)
async def update_user(data: UpdateUserModel, user: UserModel = Depends(validate_token)):
    user_data = {k: v for k, v in data.model_dump(by_alias=True, mode='json').items() if v is not None}
    password = user_data['password']

    if password:
        password = hash_password(password)
        user_data['password'] = password

    if len(user_data) >= 1:
        update_result = await user_collection.find_one_and_update(
            {"_id": ObjectId(user.id)},
            {"$set": user_data},
            return_document=ReturnDocument.AFTER,
        )

        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User {user.id} not found")
        
    if (existing_user := await user_collection.find_one({"_id": user.id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {user.id} not found")

@users_router.delete(
    '/',
    status_code=204,
    response_description='Delete a user'
)
async def delete_user(user: UserModel = Depends(validate_token)):
    delete_result = await user_collection.delete_one(
        { '_id': ObjectId(user.id) }
    )
    if delete_result.deleted_count == 0:
        return HTTPException(status_code=404, detail=f"User {user.id} not found")