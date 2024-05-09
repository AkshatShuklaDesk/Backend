from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class AddressTypeBase(SQLModel):
    pass

class AddressTypeCreate(AddressTypeBase):
    pass

class AddressTypeUpdate(AddressTypeBase):
    pass

class AddressType(AddressTypeBase, table=True):
    __tablename__ = "address_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
