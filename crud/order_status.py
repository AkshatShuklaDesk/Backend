from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.order_status import OrderStatus, OrderStatusCreate, OrderStatusBase


class CRUDOrderStatus(CRUDBase[OrderStatus, OrderStatusCreate, OrderStatusBase]):
    def get_by_name(self,db:Session,name):
        order_status = db.query(self.model).filter(self.model.name==name).first()
        return order_status

    def get_base_status(self,db:Session):
        base_status = db.query(self.model).filter(self.model.parent_id != None).all()
        return {**jsonable_encoder(base_status)}


order_status = CRUDOrderStatus(OrderStatus)
