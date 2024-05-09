import datetime
from typing import List
import collections
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import operator
from sqlalchemy import or_
import crud
from sqlalchemy.sql import func
from models import Product, WeightFreezeStatus
from crud.base import CRUDBase
from models.weight_freeze import WeightFreeze, WeightFreezeCreate, WeightFreezeBase


class CRUDWeightFreeze(CRUDBase[WeightFreeze, WeightFreezeCreate, WeightFreezeBase]):
    def create_weight_freeze(self,db:Session,obj_in,user_id):
        image_urls = obj_in.pop('images')
        prod_obj = crud.product.get(db=db,id=obj_in['product_id'])
        prod_obj_in = {'id':obj_in['product_id'],**image_urls}
        crud.product.update(db=db, obj_in=prod_obj_in, db_obj=prod_obj)
        obj_in['status_id'] = crud.weight_freeze_status.get_by_name(db=db,name=obj_in.pop('status_name')).id
        obj_in['created_by'] = obj_in['modified_by'] = user_id
        obj_in['created_date'] = obj_in['modified_date'] = datetime.datetime.now()
        result = self.create(db=db, obj_in=obj_in)
        return result

    def update_weight_freeze(self,db:Session,obj_in,user_id,id):
        image_urls = obj_in.pop('images')
        if image_urls:
            prod_obj = crud.product.get(db=db, id=obj_in['product_id'])
            prod_obj_in = {'id': obj_in['product_id'], **image_urls}
            crud.product.update(db=db, obj_in=prod_obj_in, db_obj=prod_obj)
        weight_freeze_obj = self.get(db=db,id=id)
        obj_in['status_id'] = crud.weight_freeze_status.get_by_name(db=db,name=obj_in.pop('status_name')).id
        obj_in['modified_by'] = user_id
        obj_in['modified_date'] = datetime.datetime.now()
        result = self.update(db=db, db_obj=weight_freeze_obj, obj_in=obj_in)
        return result

    def get_weight_freeze_products(self,db:Session,user_id,filter_fields=None,date_from=None,date_to=None,page=None,
            per_page=None):

        fields_dict = {
            "status_name": WeightFreezeStatus.name,
            "status_id": WeightFreezeStatus.id,
            "search": Product.name
        }

        filter_list = [Product.created_by == user_id]
        if date_from:
            filter_list.append(func.DATE(self.model.created_date) >= date_from)

        if date_to:
            filter_list.append(func.DATE(self.model.created_date) <= date_to)

        for field, value in filter_fields.items():
            if field in fields_dict and value:
                if field == 'search':
                    srch = "%{}%".format(value.lower())
                    filter_list.append(or_(Product.name.ilike(srch),Product.sku.ilike(srch)))
                elif value == "Not Requested":
                    product_ids = list(map(operator.itemgetter(0),
                                           db.query(self.model.product_id).distinct(self.model.product_id).filter(
                                               *filter_list).all()))
                    filter_list.append(~Product.id.in_(product_ids))
                    continue
                else:
                    filter_list.append(fields_dict[field] == value)

        query = db.query(Product, self.model, WeightFreezeStatus.name).select_from(Product). \
            outerjoin(self.model, self.model.product_id == Product.id). \
            outerjoin(WeightFreezeStatus, WeightFreezeStatus.id == self.model.status_id)

        # query_in = db.query(Product, self.model, WeightFreezeStatus.name).select_from(Product). \
        #     join(self.model, self.model.product_id == Product.id). \
        #     join(WeightFreezeStatus, WeightFreezeStatus.id == self.model.status_id)

        query = query.filter(*filter_list)
        total_entries = len(query.all())
        all_products = query.limit(per_page).offset((page - 1) * per_page).all()

        result = []

        for product in all_products:
            temp = {}
            temp['id'] = product[0].id
            temp['name'] = product[0].name
            temp['sku'] = product[0].sku
            temp['channel_name'] = "CUSTOM" # temp set as we don't have channel in product
            temp['status_name'] = "Not Requested" if not product[2] else product[2]
            temp['status_id'] = None if not product[1] else product[1].status_id
            temp['images'] = [product[0].img_1,product[0].img_2] # temp added as we need to define how to respone images
            temp['package_details'] = {'length':product[1].length if product[1] else 0,
                                       'width':product[1].width if product[1] else 0,
                                       'height':product[1].height if product[1] else 0,
                                       'dead_weight':product[1].weight if product[1] else 0}
            result.append(temp)
        return {'total_rows':total_entries,'data':result}

    def get_status_wise_count(self,db:Session,user_id):
        query = db.query(Product, self.model, WeightFreezeStatus.name). \
            outerjoin(self.model, self.model.product_id == Product.id). \
            outerjoin(WeightFreezeStatus, WeightFreezeStatus.id == self.model.status_id).filter(Product.created_by == user_id)

        all_products = query.all()

        result = []

        for product in all_products:
            temp = {}
            temp['id'] = product[0].id
            temp['name'] = product[0].name
            temp['sku'] = product[0].sku
            temp['channel_name'] = "CUSTOM"  # temp set as we don't have channel in product
            temp['status_name'] = "Not Requested" if not product[2] else product[2]
            temp['status_id'] = None if not product[1] else product[1].status_id
            temp['images'] = [product[0].img_1,
                              product[0].img_2]  # temp added as we need to define how to respone images
            temp['package_details'] = {'length': product[1].length if product[1] else 0,
                                       'width': product[1].width if product[1] else 0,
                                       'height': product[1].height if product[1] else 0,
                                       'dead_weight': product[1].weight if product[1] else 0}
            result.append(temp)
        data = dict(collections.Counter([d['status_name'] for d in result]))
        return data

    def create_weight_freeze_from_file(self,db,obj_in,user_id):
        already_exist_products = []
        for product_freeze_info in obj_in:
            new = {}
            new['product'] = {'name': product_freeze_info['name'],
                              'sku': product_freeze_info['sku'],
                              'img1': product_freeze_info['img1'],
                              'img2': product_freeze_info['img1'],
                              'length_img': product_freeze_info['length_img'],
                              'width_img': product_freeze_info['width_img'],
                              'height_img': product_freeze_info['height_img'],
                              'weight_img': product_freeze_info['weight_img']}
            new['freeze'] = {'status_name': product_freeze_info['status'],
                             'length': product_freeze_info['length'],
                             'width': product_freeze_info['width'],
                             'height': product_freeze_info['height'],
                             'weight': product_freeze_info['weight']}

            test = new['freeze']
            sku_pro = crud.product.get_from_sku(db=db,sku=str(new['product']['sku']))
            if sku_pro:
                already_exist_products.append(new['product'])
                continue

            new['product']['created_by'] = new['product']['modified_by'] = user_id
            new['product']['created_date'] = new['product']['modified_date'] = datetime.datetime.now()
            product = crud.product.create(db=db,obj_in=new['product'])
            if new['freeze']['status_name'] != 'Not Requested':
                new['freeze']['status_id'] = crud.weight_freeze_status.get_by_name(db=db,name=new['freeze'].pop('status_name')).id
                new['freeze']['product_id'] = product.id
                new['freeze']['created_by'] = new['freeze']['modified_by'] = user_id
                new['freeze']['created_date'] = new['freeze']['modified_date'] = datetime.datetime.now()
                self.create(db=db,obj_in=new['freeze'])
        return {'success': True, 'already_exists_products': already_exist_products}

weight_freeze = CRUDWeightFreeze(WeightFreeze)
