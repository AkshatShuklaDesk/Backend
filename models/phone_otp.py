from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT,BigInteger
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel
from datetime import datetime

class PhoneOtpBase(SQLModel):
    pass

class PhoneOtpCreate(PhoneOtpBase):
    pass

class PhoneOtpUpdate(PhoneOtpBase):
    pass

class PhoneOtp(PhoneOtpBase, table=True):
    __tablename__ = "phone_otp"

    id: Optional[int] = Field(default=None, primary_key=True)
    phone_no: Optional[int]
    otp: Optional[int]
    is_verified: Optional[bool]
    expiry_time: Optional[str]
    users_id: Optional[int]
    created_date : Optional[datetime]
