from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.order_product import OrderProduct, OrderProductCreate, OrderProductBase


class CRUDOrderProduct(CRUDBase[OrderProduct, OrderProductCreate, OrderProductBase]):
    def create_multiple_order_products(self,db:Session,order_id,products):
        input_list = []
        for prod in products:
            prod_dict = jsonable_encoder(prod)
            input_list.append({'order_id':order_id,'product_id':prod_dict.pop('id'),**prod_dict})
        self.create_multi(db=db,obj_in=input_list)


order_product = CRUDOrderProduct(OrderProduct)
