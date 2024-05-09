from typing import Literal, Optional
from datetime import date, datetime, time
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    model_validator,
)

from schemas.common import PHONE_REGEX


class CreateShipment(BaseModel):
    name: str = Field()
    phone: str = Field(pattern=PHONE_REGEX, min_length=7)
    address: str = Field(serialization_alias="add")
    pincode: str = Field(pattern=r"^\d+$", serialization_alias="pin")
    city: Optional[str] = Field(default="")
    state: Optional[str] = Field(default="")
    country: Optional[str] = Field(default="")
    address_type: Optional[Literal["Home", "Office"]] = Field(default="")
    payment_mode: Literal["Pickup", "Prepaid", "COD", "REPL"] = Field()
    order_id: str = Field(serialization_alias="order")
    shipment_mode: Literal["Express", "Surface"] = Field()

    weight: Optional[str] = Field(default="")
    products_desc: Optional[str] = Field(default="")
    hsn_code: Optional[str] = Field(default="")
    amount: Optional[str] = Field(default="", serialization_alias="cod_amount")
    order_date: Optional[str] = Field(default="")
    total_amount: Optional[str] = Field(default="")
    seller_address: Optional[str] = Field(default="", serialization_alias="seller_add")
    seller_name: Optional[str] = Field(default="")
    seller_inv: Optional[str] = Field(default="")
    quantity: Optional[str] = Field(default="")
    waybill: Optional[str] = Field(default="")
    width: Optional[str] = Field(default="", serialization_alias="shipment_width")
    height: Optional[str] = Field(default="", serialization_alias="shipment_height")
    seller_gst_tin: Optional[str] = Field(default="")

    # return things required only when shipment type isn't forward
    return_address: Optional[str] = Field(default="", serialization_alias="return_add")
    return_phone: Optional[str] = Field(default="")
    return_pincode: Optional[str] = Field(default="", serialization_alias="return_pin")
    return_city: Optional[str] = Field(default="")
    return_state: Optional[str] = Field(default="")
    return_country: Optional[str] = Field(default="India")

    # add fragile_shipment key with boolean value if needed
    @model_validator(mode="after")
    def check_cod_amount(self):
        if self.payment_mode == "COD" and (
            self.amount is None or float(self.amount) <= 0
        ):
            raise ValueError('amount is required when payment_mode is "COD"')
        return self


class UpdateShipment(BaseModel):
    phone: Optional[str] = Field(default=None, pattern=PHONE_REGEX)
    name: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None, serialization_alias="add")
    product_details: Optional[str] = Field(default=None)
    length: Optional[float] = Field(default=None, serialization_alias="shipment_length")
    width: Optional[float] = Field(default=None, serialization_alias="shipment_width")
    height: Optional[float] = Field(default=None, serialization_alias="shipment_height")
    weight: Optional[str] = Field(default=None)
    payment_mode: Optional[Literal["Pre-paid", "COD"]] = Field(
        default=None, serialization_alias="pt"
    )
    amount: Optional[int] = Field(default=None, serialization_alias="cod")

    @model_validator(mode="after")
    def check_cod_amount(self):
        if self.payment_mode == "COD" and self.amount is None:
            raise ValueError('amount is required when payment_mode is "COD"')
        return self


class GetShippingCost(BaseModel):
    billing_mode: Literal["Express", "Surface"] = Field(serialization_alias="md")
    status: Literal["Delivered", "RTO", "DTO"] = Field(serialization_alias="ss")
    origin_pincode: str = Field(serialization_alias="o_pin")
    dest_pincode: str = Field(serialization_alias="d_pin")
    weight: str = Field(serialization_alias="cgm")
    payment_mode: Literal["COD", "Pre-paid", "Pickup", "REPL"] = Field(
        serialization_alias="pt"
    )
    amount: Optional[str] = Field(default=None, serialization_alias="cod")

    @field_serializer("billing_mode")
    def ser_model(self, billing_mode: Literal["Express", "Surface"]):
        return billing_mode[0]

    @model_validator(mode="after")
    def check_cod_amount(self):
        if self.payment_mode == "COD" and self.amount is None:
            raise ValueError('amount is required when payment_mode is "COD"')
        return self


class PickupDateTime(BaseModel):
    pickup_time: time
    pickup_date: date

    @field_serializer("pickup_time")
    def ser_model(self, pickup_time: time):
        return pickup_time.isoformat().split(".")[0]

    # @model_validator(mode="after")
    # def check_cod_amount(self):
    #     dt = datetime.fromisoformat(
    #         self.pickup_date.isoformat() + "T" + self.pickup_time.isoformat()
    #     )
    #     # if dt.timestamp() <= datetime.now().timestamp():
    #     #     raise ValueError("Pickup date and time must be in future")
    #     return self


class PickupDetail(PickupDateTime):
    pickup_location: str
    expected_package_count: int = Field(gt=0)
