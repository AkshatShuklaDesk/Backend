from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class PackageTypeBase(SQLModel):
    pass

class PackageTypeCreate(PackageTypeBase):
    pass

class PackageTypeUpdate(PackageTypeBase):
    pass

class PackageType(PackageTypeBase, table=True):
    __tablename__ = "package_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
