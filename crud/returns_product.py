from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.returns_product import ReturnsProduct, ReturnsProductCreate, ReturnsProductBase


class CRUDReturnsProduct(CRUDBase[ReturnsProduct, ReturnsProductCreate, ReturnsProductBase]):
    def create_multiple_return_products(self,db:Session,order_id,products):
        input_list = []
        for prod in products:
            prod_dict = jsonable_encoder(prod)
            input_list.append({
                'product_id': prod_dict.pop('id'),
                'return_id': order_id,
                **prod_dict,
            })
        self.create_multi(db=db, obj_in=input_list)


returns_product = CRUDReturnsProduct(ReturnsProduct)
