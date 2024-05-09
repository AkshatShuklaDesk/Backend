from typing import List, Optional
from pydantic import BaseModel


class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    ebill_number: Optional[str] = None
    ebill_expiry_date: Optional[str] = None

class OrderItem(BaseModel):
    product_name: Optional[str] = None
    product_qty: Optional[str] = None
    product_price: Optional[str] = None
    product_tax_per: Optional[str] = None
    product_sku: Optional[str] = None
    product_hsn: Optional[str] = None

class ShipmentRequest(BaseModel):
    order_number: Optional[str] = None
    payment_method: Optional[str] = None
    consigner_name: Optional[str] = None
    consigner_phone: Optional[str] = None
    consigner_pincode: Optional[str] = None
    consigner_city: Optional[str] = None
    consigner_state: Optional[str] = None
    consigner_address: Optional[str] = None
    consigner_gst_number: Optional[str] = None
    consignee_name: Optional[str] = None
    consignee_phone: Optional[str] = None
    consignee_pincode: Optional[str] = None
    consignee_city: Optional[str] = None
    consignee_state: Optional[str] = None
    consignee_address: Optional[str] = None
    consignee_gst_number: Optional[str] = None
    products: Optional[List[OrderItem]] = None
    invoice: Optional[List[Invoice]] = None
    weight: Optional[str] = None
    length: Optional[str] = None
    height: Optional[str] = None
    breadth: Optional[str] = None
    courier_id: Optional[str] = None
    pickup_location: Optional[str] = None
    shipping_charges: Optional[float] = None
    cod_charges: Optional[float] = None
    discount: Optional[float] = None
    order_amount: Optional[float] = None
    collectable_amount: Optional[float] = None

class XpressEstimation(BaseModel):
    origin: int
    destination: int
    payment_type: str
    order_amount: Optional[float]
    weight: Optional[float]
    length:Optional[int]
    breadth:Optional[int]
    height:Optional[int]


class Consignee(BaseModel):
    name: Optional[str]
    address: Optional[str]
    address_2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    phone: Optional[str]
    alternate_phone: Optional[str]

class Pickup(BaseModel):
    warehouse_name: Optional[str]
    name: Optional[str]
    address: Optional[str]
    address_2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    phone: Optional[str]

class ReturnShipment(BaseModel):
    order_id: Optional[str]
    request_auto_pickup: Optional[str]
    consignee: Optional[Consignee]
    pickup: Optional[Pickup]
    categories: Optional[str]
    product_name: Optional[str]
    product_qty: Optional[str]
    product_amount: Optional[str]
    package_weight: Optional[int]
    package_length: Optional[str]
    package_breadth: Optional[str]
    package_height: Optional[str]
    qccheck: Optional[str]
    uploadedimage: Optional[str]
    uploadedimage_2: Optional[str]
    uploadedimage_3: Optional[str]
    uploadedimage_4: Optional[str]
    product_usage: Optional[str]
    product_damage: Optional[str]
    brandname: Optional[str]
    brandnametype: Optional[str]
    productsize: Optional[str]
    productsizetype: Optional[str]
    productcolor: Optional[str]
    productcolourtype: Optional[str]