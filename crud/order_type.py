from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.order_type import OrderType, OrderTypeCreate, OrderTypeBase


class CRUDOrderType(CRUDBase[OrderType, OrderTypeCreate, OrderTypeBase]):
    def get_by_name(self,db:Session,name):
        order_type = db.query(self.model).filter(self.model.name==name).first()
        return order_type
    pass


order_type = CRUDOrderType(OrderType)
