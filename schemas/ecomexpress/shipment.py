from typing import List, Optional
from pydantic import BaseModel, Field

class AdditionalInformation(BaseModel):
    GST_TAX_CGSTN: Optional[str] = None
    GST_TAX_IGSTN: Optional[str] = None
    GST_TAX_SGSTN: Optional[str] = None
    SELLER_GSTIN: Optional[str] = None
    INVOICE_DATE: Optional[str] = None
    INVOICE_NUMBER: Optional[str] = None
    GST_TAX_RATE_SGSTN: Optional[str] = None
    GST_TAX_RATE_IGSTN: Optional[str] = None
    GST_TAX_RATE_CGSTN: Optional[str] = None
    GST_HSN: Optional[str] = None
    GST_TAX_BASE: Optional[str] = None
    GST_ERN: Optional[str] = None
    ESUGAM_NUMBER: Optional[str] = None
    ITEM_CATEGORY: Optional[str] = None
    GST_TAX_NAME: Optional[str] = None
    ESSENTIALPRODUCT: Optional[str] = None
    PICKUP_TYPE: Optional[str] = None
    OTP_REQUIRED_FOR_DELIVERY: Optional[str] = None
    RETURN_TYPE: Optional[str] = None
    GST_TAX_TOTAL: Optional[str] = None
    SELLER_TIN: Optional[str] = None
    CONSIGNEE_ADDRESS_TYPE: Optional[str] = None
    CONSIGNEE_LONG: Optional[str] = None
    CONSIGNEE_LAT: Optional[str] = None
    what3words: Optional[str] = None

class ShipmentRequest(BaseModel):
    AWB_NUMBER: str
    ORDER_NUMBER: str
    PRODUCT: str
    CONSIGNEE: str
    CONSIGNEE_ADDRESS1: str
    CONSIGNEE_ADDRESS2: Optional[str] = None
    CONSIGNEE_ADDRESS3: Optional[str] = None
    DESTINATION_CITY: str
    PINCODE: str
    STATE: str
    MOBILE: str
    TELEPHONE: Optional[str] = None
    ITEM_DESCRIPTION: str
    PIECES: int
    COLLECTABLE_VALUE: float
    DECLARED_VALUE: float
    ACTUAL_WEIGHT: float
    VOLUMETRIC_WEIGHT: Optional[float]=0
    LENGTH: Optional[float]
    BREADTH: Optional[float]
    HEIGHT: Optional[float]
    PICKUP_NAME: str
    PICKUP_ADDRESS_LINE1: str
    PICKUP_ADDRESS_LINE2: Optional[str] = None
    PICKUP_PINCODE: str
    PICKUP_PHONE: str
    PICKUP_MOBILE: str
    RETURN_NAME: str
    RETURN_ADDRESS_LINE1: str
    RETURN_ADDRESS_LINE2: Optional[str] = None
    RETURN_PINCODE: str
    RETURN_PHONE: str
    RETURN_MOBILE: str
    DG_SHIPMENT: str

# json_input: List[ShipmentRequest]
    
class OrderEstimation(BaseModel):
    orginPincode: int
    destinationPincode: int
    productType: str
    chargeableWeight: float
    codAmount: float


class AdditionalInformationReturn(BaseModel):
    SELLER_TIN: Optional[str]
    INVOICE_NUMBER: Optional[str]
    INVOICE_DATE: Optional[str]
    ESUGAM_NUMBER: Optional[str]
    ITEM_CATEGORY: Optional[str]
    PACKING_TYPE: Optional[str]
    PICKUP_TYPE: Optional[str]
    RETURN_TYPE: Optional[str]
    PICKUP_LOCATION_CODE: Optional[str]
    SELLER_GSTIN: Optional[str]
    GST_HSN: Optional[str]
    GST_ERN: Optional[str]
    GST_TAX_NAME: Optional[str]
    GST_TAX_BASE: Optional[float]
    GST_TAX_RATE_CGSTN: Optional[float]
    GST_TAX_RATE_SGSTN: Optional[float]
    GST_TAX_RATE_IGSTN: Optional[float]
    GST_TAX_TOTAL: Optional[float]
    GST_TAX_CGSTN: Optional[str]
    GST_TAX_SGSTN: Optional[str]
    GST_TAX_IGSTN: Optional[str]
    DISCOUNT: Optional[str]
    PICKUP_DATE: Optional[str]

class ShipmentReturn(BaseModel):
    AWB_NUMBER: Optional[str] = ""
    ORDER_NUMBER: Optional[str] = ""
    PRODUCT: Optional[str] = ""
    REVPICKUP_NAME: Optional[str] = ""
    REVPICKUP_ADDRESS1: Optional[str] = ""
    REVPICKUP_ADDRESS2: Optional[str] = ""
    REVPICKUP_ADDRESS3: Optional[str] = ""
    REVPICKUP_CITY: Optional[str] = ""
    REVPICKUP_PINCODE: Optional[str] = ""
    REVPICKUP_STATE: Optional[str] = ""
    REVPICKUP_MOBILE: Optional[str] = ""
    REVPICKUP_TELEPHONE: Optional[str] = ""
    PIECES: Optional[str] = ""
    COLLECTABLE_VALUE: Optional[str] = ""
    DECLARED_VALUE: Optional[str] = ""
    ACTUAL_WEIGHT: Optional[str] = ""
    VOLUMETRIC_WEIGHT: Optional[str] = ""
    LENGTH: Optional[str] = ""
    BREADTH: Optional[str] = ""
    HEIGHT: Optional[str] = ""
    VENDOR_ID: Optional[str] = ""
    DROP_NAME: Optional[str] = ""
    DROP_ADDRESS_LINE1: Optional[str] = ""
    DROP_ADDRESS_LINE2: Optional[str] = ""
    DROP_PINCODE: Optional[str] = ""
    DROP_MOBILE: Optional[str] = ""
    ITEM_DESCRIPTION: Optional[str] = ""
    DROP_PHONE: Optional[str] = ""
    EXTRA_INFORMATION: Optional[str] = ""
    DG_SHIPMENT: Optional[str] = ""
    ADDITIONAL_INFORMATION: Optional[AdditionalInformationReturn]  = None

class EcomexpressObjectsReturn(BaseModel):
    SHIPMENT: ShipmentReturn