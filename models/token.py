from pydantic import BaseModel, EmailStr
from typing import Union

class Token(BaseModel):
    access_token: str
    token_type: str


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: Union[int, None] = None