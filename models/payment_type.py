from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class PaymentTypeBase(SQLModel):
    pass

class PaymentTypeCreate(PaymentTypeBase):
    pass

class PaymentTypeUpdate(PaymentTypeBase):
    pass

class PaymentType(PaymentTypeBase, table=True):
    __tablename__ = "payment_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
