from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.payment_type import PaymentType, PaymentTypeCreate, PaymentTypeBase


class CRUDPaymentType(CRUDBase[PaymentType, PaymentTypeCreate, PaymentTypeBase]):
    def get_by_name(self,db:Session,name):
        type = db.query(self.model).filter(self.model.name == name).first()
        return type
    pass


payment_type = CRUDPaymentType(PaymentType)
