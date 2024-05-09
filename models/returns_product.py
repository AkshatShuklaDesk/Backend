from sqlalchemy import Boolean, FLOAT,Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class ReturnsProductBase(SQLModel):
    pass

class ReturnsProductCreate(ReturnsProductBase):
    pass

class ReturnsProductUpdate(ReturnsProductBase):
    pass

class ReturnsProduct(ReturnsProductBase, table=True):
    __tablename__ = "returns_product"

    id: Optional[int] = Field(default=None, primary_key=True)
    return_id: Union[int, None] = Field(
        default=None, foreign_key="returns.id"
    )
    product_id: Union[int, None] = Field(
        default=None, foreign_key="product.id"
    )
    unit_price: Optional[int]
    quantity: Optional[int]
    category_tax: Optional[float]
    brand: Optional[str]
    color: Optional[str]
