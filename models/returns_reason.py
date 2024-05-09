from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class ReturnsReasonBase(SQLModel):
    pass

class ReturnsReasonCreate(ReturnsReasonBase):
    pass

class ReturnsReasonUpdate(ReturnsReasonBase):
    pass

class ReturnsReason(ReturnsReasonBase, table=True):
    __tablename__ = "returns_reason"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
