from pydantic import BaseModel, HttpUrl, EmailStr, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing import Optional, Annotated, Literal, Union
from bson import ObjectId
from datetime import date

PyObjectId = Annotated[str, BeforeValidator(str)]

class LoginSecretBase(BaseModel):
    type: Literal['login']
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    sites: Optional[list[HttpUrl]] = None

class LoginSecret(LoginSecretBase):
    email: EmailStr = None
    password: str = None

class LoginSecretUpdate(LoginSecretBase):
    pass

class CreditCardSecretBase(BaseModel):
    type: Literal['credit_card']
    full_name: Optional[str] = None
    card_number: Optional[str] = None
    expire_date: Optional[date] = None
    security_code: Optional[str] = None
    pin_number: Optional[str] = None

class CreditCardSecret(CreditCardSecretBase):
    full_name: str = None
    card_number: str = None
    expire_date: date = None
    security_code: str = None
    pin_number: str = None

class CreditCardSecretUpdate(CreditCardSecretBase):
    pass

class FileSecretBase(BaseModel):
    type: Literal['file']
    file_path: Optional[str] = None

class FileSecret(FileSecretBase):
    file_path: str = None

class FileSecretUpdate(FileSecretBase):
    pass

SecretContent = Union[LoginSecret, CreditCardSecret, FileSecret]
SecretContentUpdate = Union[LoginSecretUpdate, CreditCardSecretUpdate, FileSecretUpdate]

class SecretModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    name: str = Field(...)
    content: SecretContent = None
    description: str | None = None  
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class UpdateSecretModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[SecretContentUpdate] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ ObjectId: str }
    )

class SecretCollection(BaseModel):
    secrets: list[SecretModel]