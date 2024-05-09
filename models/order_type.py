from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class OrderTypeBase(SQLModel):
    pass

class OrderTypeCreate(OrderTypeBase):
    pass

class OrderTypeUpdate(OrderTypeBase):
    pass

class OrderType(OrderTypeBase, table=True):
    __tablename__ = "order_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
