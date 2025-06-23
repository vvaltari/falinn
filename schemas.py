from pydantic import BaseModel, HttpUrl, Field, ConfigDict, EmailStr
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class UpdateUserModel(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ ObjectId: str }
    )

class UserCollection(BaseModel):
    users: list[UserModel]

class SecretModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str = Field(...)
    secret: str = Field(...)
    description: str | None = None  
    sites: Optional[list[HttpUrl]] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class UpdateSecretModel(BaseModel):
    name: Optional[str] = None
    secret: Optional[str] = None
    description: Optional[str] = None  
    sites: Optional[list[HttpUrl]] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ ObjectId: str }
    )

class SecretCollection(BaseModel):
    secrets: list[SecretModel]