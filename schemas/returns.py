from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from schemas.order import AddressDetail, AddressInfo, ProductInfo, UserInfo


class ReturnCreate(BaseModel):
    return_id: Optional[str]
    return_reason: Optional[str] = None
    buyer_info: Optional[UserInfo] = None
    address_info: Optional[AddressDetail] = None
    pickup_address: Optional[AddressInfo] = None
    partner_name: Optional[str] = None
    date: Optional[datetime] = None
    channel: Optional[str] = None
    order_id: Optional[str] = None
    product_info: Optional[List[ProductInfo]] = None
    dead_weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    total_amount: Optional[float] = None
    volumatric_package_id: Optional[float] = None
    volumatric_weight: Optional[float] = None
    applicable_weight: Optional[float] = None


class ReturnUpdate(BaseModel):
    buyer_info: Optional[UserInfo] = None
    date: Optional[datetime] = None
    channel: Optional[str] = None
    status: Optional[str] = None
    product_info: Optional[List[ProductInfo]] = None
    pickup_address_id: Optional[int] = None
    drop_address_id: Optional[int] = None
    dead_weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    total_amount: Optional[float] = None
    volumatric_weight: Optional[float] = None
    applicable_weight: Optional[float] = None
