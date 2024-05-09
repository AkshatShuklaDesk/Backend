from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT,FLOAT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel
from datetime import datetime

class ReturnsBase(SQLModel):
    pass

class ReturnsCreate(ReturnsBase):
    pass

class ReturnsUpdate(ReturnsBase):
    pass

class Returns(ReturnsBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    return_id: Optional[str]
    waybill_no: Optional[str]
    users_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    status_id: Union[int, None] = Field(
        default=None, foreign_key="returns_status.id"
    )
    buyer_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    date: Optional[str]
    returns_reason_id: Union[int, None] = Field(
        default=None, foreign_key="returns_reason.id"
    )
    comments: Optional[str]
    channel: Optional[str]
    payment_type_id: Union[int, None] = Field(
        default=None, foreign_key="payment_type.id"
    )
    discount: Optional[float]
    sub_total: Optional[float]
    other_charges: Optional[float]
    total_amount: Optional[float]
    dead_weight: Optional[float]
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]
    volumatric_package_id: Union[int, None] = Field(
        default=None, foreign_key="package.id"
    )
    volumatric_weight: Optional[float]
    applicable_weight: Optional[float]
    partner_id: Optional[int] = Field(default=None, foreign_key="partner.id")
    pickup_id: Optional[int]
    order_id: Union[int, None] = Field(
        default=None, foreign_key="order.id"
    )
    pickup_address_id: Union[int, None] = Field(
        default=None, foreign_key="address.id"
    )
    drop_address_id: Union[int, None] = Field(
        default=None, foreign_key="address.id"
    )
    created_date: datetime = Field(default=datetime.utcnow(), nullable=False)
    modified_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)

