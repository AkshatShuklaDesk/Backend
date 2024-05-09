from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.payment_status_details import PaymentStatusDetails, PaymentStatusDetailsCreate, PaymentStatusDetailsBase


class CRUDPaymentStatusDetails(CRUDBase[PaymentStatusDetails, PaymentStatusDetailsCreate, PaymentStatusDetailsBase]):
    def get_by_payment_order_id(self,db:Session,order_id):
        payment_status_details = db.query(self.model).filter(self.model.payment_order_id==order_id).first()
        return payment_status_details


payment_status_details = CRUDPaymentStatusDetails(PaymentStatusDetails)
