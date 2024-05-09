from typing import List,Dict

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.buyer_seller_map import BuyerSellerMap, BuyerSellerMapCreate, BuyerSellerMapBase


class CRUDBuyerSellerMap(CRUDBase[BuyerSellerMap, BuyerSellerMapCreate, BuyerSellerMapBase]):
    def get_company_from_name(self,db:Session,name):
        company = db.query(self.model).filter(self.model.name == name).first()
        return company

    def check_and_create_company(self,db:Session,company_in:Dict):
        company = self.get_company_from_name(db=db,name=company_in['name'])
        if company:
            return company
        company = self.create(db=db,obj_in=company_in)
        return company


buyer_seller_map = CRUDBuyerSellerMap(BuyerSellerMap)
