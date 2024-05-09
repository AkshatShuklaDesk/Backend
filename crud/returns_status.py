from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.returns_status import ReturnsStatus, ReturnsStatusCreate, ReturnsStatusBase


class CRUDReturnsStatus(CRUDBase[ReturnsStatus, ReturnsStatusCreate, ReturnsStatusBase]):
    def get_by_name(self,db:Session,name):
        order_status = db.query(self.model).filter(self.model.name==name).first()
        return order_status


returns_status = CRUDReturnsStatus(ReturnsStatus)
