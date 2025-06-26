from pydantic import BaseModel, Field, ConfigDict, EmailStr
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(exclude=True)
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