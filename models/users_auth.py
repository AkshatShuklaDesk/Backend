from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class UsersAuthBase(SQLModel):
    pass

class UsersAuthCreate(UsersAuthBase):
    pass

class UsersAuthUpdate(UsersAuthBase):
    pass

class UsersAuth(UsersAuthBase, table=True):
    __tablename__ = "users_auth"

    id: Optional[int] = Field(default=None, primary_key=True)
    users_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    password: Optional[str]
    last_otp : Optional[int]
    is_admin:Optional[int]=Field(default=0)
