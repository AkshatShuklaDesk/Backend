from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.returns_reason import ReturnsReason, ReturnsReasonCreate, ReturnsReasonBase


class CRUDReturnsReason(CRUDBase[ReturnsReason, ReturnsReasonCreate, ReturnsReasonBase]):
    def get_by_name(self,db:Session,name):
        order_status = db.query(self.model).filter(self.model.name==name).first()
        return order_status


returns_reason = CRUDReturnsReason(ReturnsReason)
