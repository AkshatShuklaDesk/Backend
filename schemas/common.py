from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, PlainSerializer, computed_field


EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
PHONE_REGEX = r"^0?[1-9]\d+$"


class TrackDetail(BaseModel):
    status: str
    origin: Annotated[str, PlainSerializer(lambda x: x.capitalize(), return_type=str)]
    destination: Annotated[
        str, PlainSerializer(lambda x: x.capitalize(), return_type=str)
    ]
    timestamp: datetime


class PartnerInfo(BaseModel):
    partner_id: Optional[int]=None
    amount: Optional[float]=None
class CancelShipmentInfo(BaseModel):
    partner_id:int

class TrackingResponse(BaseModel):
    order_id: Optional[str] = None
    order_date: Optional[datetime] = None
    waybilll_no: Optional[str] = None
    partner_name: str
    details: list[TrackDetail]
    ReverseInTransit: Optional[bool] = None

    @computed_field
    def status(self) -> str:
        return self.details[-1].status if self.details else ""
