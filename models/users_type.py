from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class UsersTypeBase(SQLModel):
    pass

class UsersTypeCreate(UsersTypeBase):
    pass

class UsersTypeUpdate(UsersTypeBase):
    pass

class UsersType(UsersTypeBase, table=True):
    __tablename__ = "users_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
