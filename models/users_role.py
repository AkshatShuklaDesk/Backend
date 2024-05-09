from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel
from datetime import datetime

class UsersRoleBase(SQLModel):
    pass

class UsersRoleCreate(UsersRoleBase):
    pass

class UsersRoleUpdate(UsersRoleBase):
    pass

class UsersRole(UsersRoleBase, table=True):
    __tablename__ = "users_role"

    id: Optional[int] = Field(default=None, primary_key=True)
    users_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    module_id: Union[int, None] = Field(
        default=None, foreign_key="module.id"
    )
    created_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
