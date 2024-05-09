from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime, TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional, Union
from sqlmodel import Field, SQLModel
from datetime import datetime


class AddressBase(SQLModel):
    pass


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AddressBase):
    pass


class Address(AddressBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    users_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    is_primary: Optional[bool]
    type_id: Union[int, None] = Field(
        default=None, foreign_key="address_type.id"
    )
    tag: Optional[str]
    line1: Optional[str]
    line2: Optional[str]
    complete_address: Optional[str]
    landmark: Optional[str] = Field(default="")
    pincode: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    address_verification: Optional[str]
    last_used_order_id: Union[int, None] = Field(
        default=None, foreign_key="order.id"
    )
    created_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
