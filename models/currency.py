from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class CurrencyBase(SQLModel):
    pass

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyUpdate(CurrencyBase):
    pass

class Currency(CurrencyBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
