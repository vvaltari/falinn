from fastapi import APIRouter, HTTPException
from bson import ObjectId
from pymongo import ReturnDocument
from database.collections import user_collection
from schemas.users import PyObjectId, UserModel, StoredUserModel, UpdateUserModel, UserCollection
from auth import hash_password

users_router = APIRouter(prefix='/users')

@users_router.get(
    '/',
    response_description='List all users',
    response_model=UserCollection,
    response_model_by_alias=False
)
async def get_users():
    users = await user_collection.find().to_list()
    return UserCollection(users=users)

@users_router.get(
    '/{user_id}',
    response_description='List a user',
    response_model=UserModel,
    response_model_by_alias=False
)
async def get_user(user_id: PyObjectId):
    user = await user_collection.find_one(
        { '_id': ObjectId(user_id) }
    )
    return user

@users_router.post(
    '/',
    response_description='Create a user',
    response_model=UserModel,
    response_model_by_alias=False
)
async def create_user(user: StoredUserModel):
    hashed_password = hash_password(user.password)
    user_data = user.model_dump(exclude=['id'], mode='json')
    user_data['password'] = hashed_password
    new_user = await user_collection.insert_one(user_data)
    created_user = await user_collection.find_one({ '_id': new_user.inserted_id })
    return created_user

@users_router.put(
    '/{user_id}',
    response_description='Update a user',
    response_model=UserModel,
    response_model_by_alias=False
)
async def update_user(user_id: PyObjectId, user: UpdateUserModel):
    data = {k: v for k, v in user.model_dump(by_alias=True, mode='json').items() if v is not None}

    if len(data) >= 1:
        update_result = await user_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )

        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
    if (existing_user := await user_collection.find_one({"_id": user_id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {user_id} not found")    

@users_router.delete(
    '/{user_id}',
    status_code=204,
    response_description='Delete a user'
)
async def delete_user(user_id: PyObjectId):
    delete_result = await user_collection.delete_one(
        { '_id': ObjectId(user_id) }
    )
    if delete_result.deleted_count == 0:
        return HTTPException(status_code=404, detail=f"User {user_id} not found")