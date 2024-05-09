from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.phone_otp import PhoneOtp, PhoneOtpCreate, PhoneOtpBase


class CRUDPhoneOtp(CRUDBase[PhoneOtp, PhoneOtpCreate, PhoneOtpBase]):
    pass


phone_otp = CRUDPhoneOtp(PhoneOtp)
