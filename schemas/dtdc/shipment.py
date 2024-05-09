from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_serializer, model_validator


class Address(BaseModel):
    pincode: str
    name: str
    phone: str
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    alternate_phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class ReturnAddress(Address):
    country: Optional[str] = None
    email: Optional[str] = None


class Piece(BaseModel):
    description: Optional[str] = None
    declared_value: Optional[str] = None
    weight: Optional[str] = None
    height: Optional[str] = None
    length: Optional[str] = None
    width: Optional[str] = None


Load_Type = Literal["Document", "Non-Document"]
Service_Type = Literal[
    "STANDARD_AIR",
    "PTP1200",
    "PEP",
    "GROUND_EXPRESS",
    "SUNDAY_PTP",
    "PRIORITY",
    "PTP1400",
    "STD EXP-A"
]


class Consignment(BaseModel):
    # our customer code
    customer_code: str = "AL316"
    service_type_id: Service_Type
    origin_details: Address
    destination_details: Address
    return_details: Optional[Address] = None
    exceptional_return_details: Optional[Address] = None
    load_type: Load_Type
    product_code: Optional[str] = None
    dimension_unit: Optional[Literal["cm", "in"]] = "cm"
    length: str
    width: str
    height: str
    weight: str
    commodity_id: Optional[str] = None
    reference_number: Optional[str] = None
    description: Optional[str] = None
    cod_amount: Optional[str] = None
    cod_collection_mode: Optional[Literal["cash", "cheque", "dd"]] = None
    cod_favor_of: Optional[str] = Field(default=None)#,min_length=10)
    declared_value: Optional[str] = None
    num_pieces: Optional[str] = Field(default=None)
    eway_bill: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    consignment_type: Optional[Literal["reverse", "", "Forward"]] = ""
    customer_reference_number: Optional[str] = None
    pieces_detail: list[Piece]

    @model_validator(mode="after")
    def check_non_doc_fields(self):
        if self.load_type == "Document":
            return self
        error_msg = "{} is required for non-document load type"
        if not self.commodity_id:
            raise ValueError(error_msg.format("commodity_id"))
        if not self.declared_value:
            raise ValueError(error_msg.format("declared_value"))
        return self

    @field_serializer("load_type")
    def ser_model(self, load_type: Load_Type):
        return load_type.upper()
