from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT,FLOAT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel
from datetime import datetime

class PackageBase(SQLModel):
    pass

class PackageCreate(PackageBase):
    name: Optional[str]
    type_id: Union[int, None] = Field(
        default=None, foreign_key="package_type.id"
    )
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]

class PackageUpdate(PackageBase):
    pass

class Package(PackageBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    type_id: Union[int, None] = Field(
        default=None, foreign_key="package_type.id"
    )
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
