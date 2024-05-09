from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT,FLOAT
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class OrderBase(SQLModel):
    pass

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    pass

class Order(OrderBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[str]
    users_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    order_type_id: Union[int, None] = Field(
        default=None, foreign_key="order_type.id"
    )
    status_id: Union[int, None] = Field(
        default=None, foreign_key="order_status.id"
    )
    buyer_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    date: Optional[datetime]
    channel_id: Optional[int] = Field(default=None, foreign_key="channel.id")
    tag: Optional[str]
    reseller_name: Optional[str]
    channel_invoice_date: Optional[datetime]
    payment_transaction_id: Optional[str]
    website_url: Optional[str]
    pickup_address_id: Union[int, None] = Field(
        default=None, foreign_key="address.id"
    )
    shipment_purpose_id: Union[int, None] = Field(
        default=None, foreign_key="shipment_purpose.id"
    )
    currency_id: Union[int, None] = Field(
        default=None, foreign_key="currency.id"
    )
    payment_type_id: Union[int, None] = Field(
        default=None, foreign_key="payment_type.id"
    )
    shipping_charges: Optional[float]
    gift_wrap: Optional[float]
    transaction_fees: Optional[float]
    discount: Optional[float]
    sub_total: Optional[float]
    other_charges: Optional[float]
    total_amount: Optional[float]
    dead_weight: Optional[float]
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]
    comment: Optional[str]
    volumatric_package_id: Union[int, None] = Field(
        default=None, foreign_key="package.id"
    )
    volumatric_weight: Optional[float]
    applicable_weight: Optional[float]
    shipped_date: Optional[str]
    invoice_generate_date: Optional[str]
    waybill_no: Optional[str]
    drop_address_id: Union[int, None] = Field(
        default=None, foreign_key="address.id"
    )
    partner_id: Union[int,None] = Field(default=None, foreign_key="partner.id")
    pickup_id: Optional[int]
    created_date: Optional[datetime]
    modified_date: Optional[datetime]

