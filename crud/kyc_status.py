from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.kyc_status import KycStatus, KycStatusCreate, KycStatusBase


class CRUDKycStatus(CRUDBase[KycStatus, KycStatusCreate, KycStatusBase]):
    pass


kyc_status = CRUDKycStatus(KycStatus)
