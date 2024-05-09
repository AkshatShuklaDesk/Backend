from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class ReturnsStatusBase(SQLModel):
    pass

class ReturnsStatusCreate(ReturnsStatusBase):
    pass

class ReturnsStatusUpdate(ReturnsStatusBase):
    pass

class ReturnsStatus(SQLModel, table=True):
    __tablename__ = "returns_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    parent_id: Union[int, None] = Field(
        default=None, foreign_key="returns_status.id"
    )
