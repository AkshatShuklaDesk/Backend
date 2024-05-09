from typing import List, Optional
from pydantic import BaseModel, Field



class marutiAddress(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    address1: Optional[str] = ""
    address2: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    country: Optional[str] = ""
    zip: Optional[str] = ""
    latitude: Optional[float] = 0
    longitude: Optional[float] = 0

class LineItem(BaseModel):
    name: Optional[str] = ""
    price: Optional[int] = 0
    weight: Optional[int] = 0
    quantity: Optional[int] = 0
    sku: Optional[str] = ""
    unitPrice: Optional[int] = 0

class MarutiOrder(BaseModel):
    orderId: Optional[str] = ""
    orderSubtype: Optional[str] = "FORWARD"
    orderCreatedAt: Optional[str] = ""
    currency: Optional[str] = ""
    amount: Optional[float] = 0
    weight: Optional[float] = 0
    lineItems: Optional[List[LineItem]] = None
    paymentType: Optional[str] = ""
    paymentStatus: Optional[str] = ""
    subTotal: Optional[float] = 0
    remarks: Optional[str] = ""
    shippingAddress: Optional[marutiAddress] = None
    billingAddress: Optional[marutiAddress] = None
    pickupAddress: Optional[marutiAddress] = None
    returnAddress: Optional[marutiAddress] = None
    gst: Optional[int] = None
    deliveryPromise: Optional[str] = ""
    discountUnit: Optional[str] = ""
    discount: Optional[float] = 0
    length: Optional[float] = 0
    height: Optional[float] = 0
    width: Optional[float] = 0





class MarutiOrderEstimation(BaseModel):
    deliveryPromise: Optional[str]
    fromPincode: Optional[int]
    toPincode: Optional[int]
    weight: Optional[float]
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]