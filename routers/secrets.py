from fastapi import APIRouter, HTTPException
from database import secret_collection
from bson import ObjectId
from pymongo import ReturnDocument
from schemas import PyObjectId, SecretModel, UpdateSecretModel, SecretCollection

secrets_router = APIRouter(prefix='/secrets')

@secrets_router.get(
    '/',
    response_description='List all secrets',
    response_model=SecretCollection,
    response_model_by_alias=False
)
async def get_secrets():
    secrets = await secret_collection.find().to_list()
    return SecretCollection(secrets=secrets)

@secrets_router.get(
    '/{secret_id}',
    response_description='List a secret',
    response_model=SecretModel,
    response_model_by_alias=False
)
async def get_secret(secret_id: PyObjectId):
    secret = await secret_collection.find_one({ '_id': ObjectId(secret_id) })
    return secret

@secrets_router.post(
    '/',
    status_code=201,
    response_description='Create a secret',
    response_model=SecretModel,
    response_model_by_alias=False
)
async def create_secret(data: SecretModel):
    new_secret = await secret_collection.insert_one(
        data.model_dump(exclude=['id'], mode='json')
    )
    created_secret = await secret_collection.find_one(
        { '_id': new_secret.inserted_id }
    )
    
    return created_secret

@secrets_router.put(
    '/{secret_id}',
    response_description='Update a secret',
    response_model=SecretModel,
    response_model_by_alias=False
)
async def update_secret(secret_id: PyObjectId, data: UpdateSecretModel):
    secret = {k: v for k, v in data.model_dump(by_alias=True, mode='json').items() if v is not None}

    if len(secret) >= 1:
        update_result = await secret_collection.find_one_and_update(
            {"_id": ObjectId(secret_id)},
            {"$set": secret},
            return_document=ReturnDocument.AFTER,
        )

        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Secret {secret_id} not found")
        
    if (existing_secret := await secret_collection.find_one({"_id": secret_id})) is not None:
        return existing_secret

    raise HTTPException(status_code=404, detail=f"Secret {secret_id} not found")

@secrets_router.delete(
    '/{secret_id}',
    status_code=204,
    response_description='Delete a secret'    
)
async def delete_secret(secret_id: PyObjectId):
    delete_result = await secret_collection.delete_one({ '_id': ObjectId(secret_id) })
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Secret {secret_id} not found")
    return