from typing import Optional, Union
from sqlmodel import Field, SQLModel
from datetime import datetime

class PaymentStatusDetailsBase(SQLModel):
    pass

class PaymentStatusDetailsCreate(PaymentStatusDetailsBase):
    pass

class PaymentStatusDetailsUpdate(PaymentStatusDetailsBase):
    pass

class PaymentStatusDetails(PaymentStatusDetailsBase, table=True):
    __tablename__ = "payment_status_details"

    id: Optional[int] = Field(default=None, primary_key=True)
    payment_order_id: Optional[str]
    amount: Optional[int]
    status: Optional[str]
    user_id: Union[int, None] = Field(
        default=None, foreign_key="company.id"
    )
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
