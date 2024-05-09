import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import crud
from models import Product, WeightDiscrepancyStatus
from crud.base import CRUDBase
from models.weight_discrepancy import WeightDiscrepancy, WeightDiscrepancyCreate, WeightDiscrepancyBase


class CRUDWeightDiscrepancy(CRUDBase[WeightDiscrepancy, WeightDiscrepancyCreate, WeightDiscrepancyBase]):
    def create_weight_discrepancy(self,db:Session,obj_in,user_id):
        try:
            already_created_list = []
            for wd in obj_in:
                order_data = db.query(self.model).filter(self.model.order_id == wd['order_id']).first()
                if order_data:
                    already_created_list.append(order_data.order_id)
                    continue
                order_info = crud.order.get_order_info(db=db,id=wd['order_id'])
                excess_weight = wd['charged_weight'] - order_info['applicable_weight']
                generation_date = modified_date = datetime.datetime.now()
                created_by = modified_by = user_id
                save_obj = {**wd,'excess_weight':excess_weight,'status_id':1,'generation_date':generation_date,
                            'modified_date':modified_date, 'created_by':created_by, 'modified_by':modified_by}
                self.create(db=db,obj_in=save_obj)
            return {'success':True, 'already_created_orders':already_created_list}
        except Exception as e:
            raise e

    def update_weight_discrepancy(self,db:Session,obj_in,user_id,id):
        weight_discrepancy_obj = self.get(db=db,id=id)
        obj_in['modified_by'] = user_id
        obj_in['modified_date'] = datetime.datetime.now()
        if 'status_name' in obj_in:
            obj_in['status_id'] = crud.weight_discrepancy_status.get_by_name(db=db,name=obj_in['status_name']).id
        result = self.update(db=db, db_obj=weight_discrepancy_obj, obj_in=obj_in)
        return result

    def update_weight_discrepancy_dispute(self,db:Session,obj_in,user_id,id):
        dis_obj_in = {}
        weight_discrepancy_obj = self.get(db=db,id=id)
        dis_obj_in['modified_by'] = obj_in['modified_by'] = user_id
        dis_obj_in['modified_date'] = obj_in['modified_date'] = datetime.datetime.now()
        dis_obj_in['status_id'] = crud.weight_discrepancy_status.get_by_name(db=db,name='Dispute Raised').id
        result = self.update(db=db, db_obj=weight_discrepancy_obj, obj_in=dis_obj_in)
        prod_obj = crud.product.get(db=db,id=obj_in.pop('product_id'))
        result = crud.product.update(db=db,db_obj=prod_obj,obj_in=obj_in)
        return result


        return result

    def get_weight_discrepancy_filtered(self,db:Session,user_id):
        order_list = crud.order.get_filtered_discrepancy_orders(db=db)
        return order_list


weight_discrepancy = CRUDWeightDiscrepancy(WeightDiscrepancy)
