from typing import Any, Optional
from pydantic import BaseModel, Field

from schemas.common import EMAIL_REGEX, PHONE_REGEX


class CreateWarehouse(BaseModel):
    name: str
    email: str = Field(pattern=EMAIL_REGEX)
    phone: str = Field(pattern=PHONE_REGEX, min_length=7)
    address: str
    pincode: str = Field(serialization_alias="pin")
    city: str
    state: str
    country: str = "India"

    registered_name: Optional[str] = None
    return_address: Optional[str] = None
    return_pincode: Optional[str] = Field(None, serialization_alias="return_pin")
    return_city: Optional[str] = None
    return_state: Optional[str] = None
    return_country: Optional[str] = None

    def __init__(
        __pydantic_self__, # pyright: ignore[reportSelfClsParameterName]
        **data: Any,
    ) -> None:
        super().__init__(**data)
        if not __pydantic_self__.registered_name:
            __pydantic_self__.registered_name = __pydantic_self__.name
        if not __pydantic_self__.return_address:
            __pydantic_self__.return_address = __pydantic_self__.address
            __pydantic_self__.return_pincode = __pydantic_self__.pincode
            __pydantic_self__.return_city = __pydantic_self__.city
            __pydantic_self__.return_state = __pydantic_self__.state
            __pydantic_self__.return_country = __pydantic_self__.country


class UpdateWarehouse(BaseModel):
    pincode: Optional[str] = Field(default=None, serialization_alias="pin")
    registered_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, pattern=PHONE_REGEX, min_length=7)
