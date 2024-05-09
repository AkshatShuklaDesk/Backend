from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class OrderProductBase(SQLModel):
    pass

class OrderProductCreate(OrderProductBase):
    pass

class OrderProductUpdate(OrderProductBase):
    pass

class OrderProduct(OrderProductBase, table=True):
    __tablename__ = "order_product"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Union[int, None] = Field(
        default=None, foreign_key="order.id"
    )
    product_id: Union[int, None] = Field(
        default=None, foreign_key="product.id"
    )
    unit_price: Optional[int]
    quantity: Optional[int]
    product_package_id: Union[int, None] = Field(
        default=None, foreign_key="product_package.id"
    )
