from typing import Optional,Dict, List
from pydantic import BaseModel
from datetime import datetime

class AddressInfo(BaseModel):
    id: Optional[int] = None
    contact_no: Optional[str] = None
    first_name: Optional[str] = None
    email_address: Optional[str] = None
    complete_address: Optional[str] = None
    tag: Optional[str] = None
    landmark: Optional[str] = None
    pincode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class ProductInfo(BaseModel):
    id: Optional[int] = None
    name: Optional[str]
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    hsn_code: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    tax_rate: Optional[float] = None
    discount: Optional[float] = None

class PaymentInfo(BaseModel):
    type: Optional[str] = None
    shipping_charges: Optional[float] = None
    gift_wrap: Optional[float] = None
    transaction_fee: Optional[float] = None
    discount: Optional[float] = None

class UserInfo(BaseModel):
    id: Optional[int] = None
    contact_no: Optional[str] = None
    first_name: Optional[str] = None
    email_address: Optional[str] = None
    alternate_contact_no: Optional[str] = None

class AddressDetail(BaseModel):
    complete_address: Optional[str] = None
    landmark: Optional[str] = None
    pincode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class CompanyInfo(BaseModel):
    name: Optional[str] = None
    gst: Optional[str] = None

class OrderCreate(BaseModel):
    order_id: Optional[str]
    buyer_info: Optional[UserInfo] = None
    company_info: Optional[CompanyInfo] = None
    address_info: Optional[AddressDetail] = None
    billing_info: Optional[AddressInfo] = None
    pickup_address: Optional[AddressInfo] = None
    order_type: Optional[str] = None
    partner_name: Optional[str] = None
    date: Optional[datetime] = None
    channel: Optional[str] = None
    tag: Optional[str] = None
    reseller_name: Optional[str] = None
    product_info: Optional[List[ProductInfo]] = None
    payment_details: Optional[PaymentInfo] = None
    sub_total: Optional[int] = None
    other_charges: Optional[int] = None
    total_amount: Optional[float] = None
    dead_weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    volumatric_package_id: Optional[float] = None
    volumatric_weight: Optional[float] = None
    applicable_weight: Optional[float] = None

class OrderUpdate(BaseModel):
    buyer_info: Optional[UserInfo] = None
    order_type: Optional[str] = None
    date: Optional[datetime] = None
    channel: Optional[str] = None
    tag: Optional[str] = None
    status: Optional[str] = None
    reseller_name: Optional[str] = None
    product_info: Optional[List[ProductInfo]] = None
    payment_type_id: Optional[int] = None
    pickup_address_id: Optional[int] = None
    drop_address_id: Optional[int] = None
    sub_total: Optional[int] = None
    other_charges: Optional[int] = None
    total_amount: Optional[int] = None
    dead_weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    volumatric_weight: Optional[float] = None
    applicable_weight: Optional[float] = None


class OrderDetails(BaseModel):
    contact_no: Optional[str]
    date: Optional[str]
    channel: Optional[str]

class CustomerDetails(BaseModel):
    full_name: Optional[str]
    contact_no: Optional[str]

class PackageDetails(BaseModel):
    dead_weight: Optional[str]
    length: Optional[str]
    width: Optional[str]
    height: Optional[str]
    volumetric_weight: Optional[str]

class Payment(BaseModel):
    total_amount: Optional[str]
    type: Optional[str]

class Address(BaseModel):
    complete_address: Optional[str]
    type: Optional[str]

class OrderGetResponse(BaseModel):
    order_details: Optional[OrderDetails]
    customer_details: Optional[CustomerDetails]
    package_details: Optional[PackageDetails]
    payment: Optional[Payment]
    pickup_address: Optional[Address]
    shipping_details: Optional[Address]
    order_shipped_date: Optional[str]
    status: Optional[str]


    