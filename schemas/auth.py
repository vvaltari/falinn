from pydantic import BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class TokenModel(BaseModel):
    access_token: str = Field(...)
    token_type: str

class TokenDataModel(BaseModel):
    id: PyObjectId | None = None
