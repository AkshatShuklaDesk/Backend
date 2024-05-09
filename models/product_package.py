from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class ProductPackageBase(SQLModel):
    pass

class ProductPackageCreate(ProductPackageBase):
    pass

class ProductPackageUpdate(ProductPackageBase):
    pass

class ProductPackage(ProductPackageBase, table=True):
    __tablename__ = "product_package"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
