from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class OrderStatusBase(SQLModel):
    pass

class OrderStatusCreate(OrderStatusBase):
    pass

class OrderStatusUpdate(OrderStatusBase):
    pass

class OrderStatus(OrderStatusBase, table=True):
    __tablename__ = "order_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    parent_id: Union[int, None] = Field(
        default=None, foreign_key="order_status.id"
    )
