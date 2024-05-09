import datetime
from typing import List, Dict, Optional

from sqlalchemy.testing.pickleable import User
from sqlmodel import literal, desc
import os
import base64
from io import BytesIO
from PIL import Image
from schemas.paginate import Paginate
from fastapi import HTTPException
from sqlalchemy.sql import func

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session,aliased

from crud.base import CRUDBase
import crud
from models import OrderStatus,OrderType,PaymentType,OrderProduct,Product,Users,Address,Company,Partner,\
    WeightDiscrepancy, WeightDiscrepancyStatus
from models.order import Order, OrderCreate, OrderBase
from fastapi.encoders import jsonable_encoder
from scripts.utilities import random_with_N_digits
import constants


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderBase]):

    def get_order_info(self,db:Session,id):
        order_info = db.query(self.model,OrderStatus.name,OrderType.name,PaymentType.name,Partner.name).select_from(self.model)\
            .outerjoin(OrderType, OrderType.id == self.model.order_type_id)\
            .outerjoin(OrderStatus, OrderStatus.id == self.model.status_id) \
            .outerjoin(Partner, Partner.id == self.model.partner_id).filter(self.model.id == id)\
            .outerjoin(PaymentType, PaymentType.id == self.model.payment_type_id).filter(self.model.id == id).first()
        if order_info is None:
            return None
        result = {**jsonable_encoder(order_info[0]),
                  'partner_name': order_info[4],
                  'status_name':order_info[1],
                  'order_type_name':order_info[2],'payment_type_name':order_info[3]}
        return result

    def get_order_info_by_awb(self,db:Session,waybill_no):
        order_info = db.query(self.model,OrderStatus.name,OrderType.name,PaymentType.name,Partner.name).select_from(self.model)\
            .outerjoin(OrderType, OrderType.id == self.model.order_type_id)\
            .outerjoin(OrderStatus, OrderStatus.id == self.model.status_id) \
            .outerjoin(Partner, Partner.id == self.model.partner_id)\
            .outerjoin(PaymentType, PaymentType.id == self.model.payment_type_id).filter(self.model.waybill_no == waybill_no).first()
        if order_info is None:
            return None
        result = {**jsonable_encoder(order_info[0]),
                  'partner_name': order_info[4],
                  'status_name':order_info[1],
                  'order_type_name':order_info[2],'payment_type_name':order_info[3]}
        return result

    def get_order_info_with_discrepancy(self,db:Session,id):
        order_info = db.query(self.model,OrderStatus.name,OrderType.name,PaymentType.name,Partner.name, WeightDiscrepancy, WeightDiscrepancyStatus.name).select_from(self.model)\
            .outerjoin(OrderType, OrderType.id == self.model.order_type_id)\
            .outerjoin(OrderStatus, OrderStatus.id == self.model.status_id) \
            .outerjoin(Partner, Partner.id == self.model.partner_id).filter(self.model.id == id)\
            .outerjoin(PaymentType, PaymentType.id == self.model.payment_type_id) \
            .join(WeightDiscrepancy, WeightDiscrepancy.order_id == self.model.id) \
            .join(WeightDiscrepancyStatus, WeightDiscrepancyStatus.id == WeightDiscrepancy.status_id) \
            .filter(self.model.id == id).first()
        if order_info is None:
            return None
        result = {**jsonable_encoder(order_info[0]),
                  'partner_name': order_info[4],
                  'status_name':order_info[1],
                  'order_type_name':order_info[2],'payment_type_name':order_info[3],**jsonable_encoder(order_info[5]),
                  'discrepancy_status_name':order_info[6]}
        return result

    def get_products_by_order(self,db:Session,id):
        product_info = db.query(Product,OrderProduct.quantity,OrderProduct.unit_price).select_from(OrderProduct).outerjoin(Product, OrderProduct.product_id == Product.id)\
            .filter(OrderProduct.order_id == id).all()
        result = []
        for product in product_info:
            result.append({**jsonable_encoder(product[0]), 'quantity': product[1],'unit_price':product[2]})
        return result

    def get_buyer_info_by_order(self,db:Session,id):
        buyer_info = db.query(Users,Address,Company).select_from(self.model)\
            .outerjoin(Users, Users.id == self.model.buyer_id)\
            .outerjoin(Address, Address.id == self.model.drop_address_id) \
            .outerjoin(Company, Company.id == Users.company_id) \
            .filter(self.model.id == id).first()
        result = {**jsonable_encoder(buyer_info[0]),**jsonable_encoder(buyer_info[1]),
                  'company_name':buyer_info[2].name if buyer_info[2] else "",'company_gst':buyer_info[2].gst if buyer_info[2] else ""}
        return result

    def get_user_info_by_order(self,db:Session,id):
        user_info = db.query(Users,Address,Company).select_from(self.model)\
            .outerjoin(Users, Users.id == self.model.users_id)\
            .outerjoin(Address, Address.id == self.model.pickup_address_id) \
            .outerjoin(Company, Company.id == Users.company_id) \
            .filter(self.model.id == id).first()
        result = {**jsonable_encoder(user_info[0]), **jsonable_encoder(user_info[1]),
                  'company_name': user_info[2].name if user_info[2] else "", 'company_gst': user_info[2].gst if user_info[2] else ""}
        return result

    def create_order(self,db:Session,order_in,user,logger=None):
        try:
            order_info = jsonable_encoder(order_in)
            exist_status = crud.order.check_order_id(db=db, order_id=order_info['order_id'] ,user_id=user)
            if exist_status:
                raise ValueError(f"order_id already exists: {order_info['order_id']}")
            buyer_info = order_info['buyer_info']
            if order_info.get("company_info"):
                company = crud.company.check_and_create_company(db=db, company_in=order_info['company_info'])
                buyer_info['company_id'] = company.id
            buyer = crud.users.check_and_create_user(db=db,user_in=buyer_info)
            address_info = order_info['address_info']
            address_info['users_id'] = buyer.id
            if not address_info.get("complete_address"):
                if "line2" in address_info and address_info["line2"] is not None:
                    address_info["complete_address"]=address_info["line1"]+address_info["line2"]
                else:
                    address_info["complete_address"]=address_info["line1"] if "line1" in address_info and address_info["line1"] is not None else None
            crud.buyer_seller_map.create(db=db,obj_in={"buyer_id": buyer.id,"seller_id": user})
            address = crud.address.create(db=db,obj_in=address_info)
            if order_info["billing_info"].get("id") is not None:
                billing_address = crud.address.get(db=db, id=order_info["billing_info"]["id"])
            else:
                billing_address = crud.address.check_save_user_address(db=db, address_in=order_info['billing_info'])
            if order_info["pickup_address"].get("id") is not None:
                if not order_info["pickup_address"]["id"]:
                    raise ValueError(f"Missing location_id in order {order_info['order_id']}")
                pickup_address = crud.address.get(db=db, id=order_info["pickup_address"]["id"])
            else:
                pickup_address = crud.address.check_save_user_address(db=db, address_in=order_info['pickup_address'])
            products = crud.product.check_and_save_products(db=db,product_in=order_info['product_info'],user_id=user)
            order_info['users_id'] = user
            order_info['pickup_address_id'] = pickup_address.id
            order_info['drop_address_id'] = address.id
            order_info['status_id'] = crud.order_status.get_by_name(db=db,name='new').id
            # order_info['partner_id'] = crud.partner.get_by_name(db=db,name=order_info["partner_name"] or "Delhivery").id
            order_info['order_type_id'] = crud.order_type.get_by_name(db=db,name=order_info['order_type']).id
            order_info['buyer_id'] = buyer.id
            order_info['payment_type_id'] = crud.payment_type.get_by_name(db=db,name=order_info['payment_details']['type']).id
            order_info.update(order_info['payment_details'])
            del order_info['payment_details']
            del order_info['buyer_info']
            del order_info['company_info']
            del order_info['product_info']
            del order_info['billing_info']
            del order_info['pickup_address']
            del order_info['address_info']
            order_info['created_date'] = order_info['modified_date'] = datetime.datetime.now()
            order = self.create(db=db,obj_in=order_info)
            crud.order_product.create_multiple_order_products(db=db, order_id=order.id,products=products)
            return order
        except Exception as e:
            if logger:
                logger.info(f'Exception in create order crud function : {e}')
            raise e

    def update_order(self,db:Session,order_in,id,user=None):
        if isinstance(order_in, dict):
            order_info = jsonable_encoder(order_in)
        else:
            order_info = order_in.model_dump(exclude_unset=True)

        if order_info.get("order_type"):
            order_info['order_type_id'] = crud.order_type.get_by_name(db=db, name=order_info['order_type']).id
        order_obj = crud.order.get(db=db,id=id)
        updated_order = {}
        if order_info.get("status"):
            status = order_info.pop("status")
            order_status = crud.order_status.get_by_name(db, status)
            if not order_status:
                raise Exception(f"Invalid order status: {order_info['status']}")
            order_info['status_id'] = order_status.id
        if order_info.get("buyer_info"):
            buyer_info = order_info.pop('buyer_info')
            buyer = crud.users.update_user_info(db=db,user_in=buyer_info)
            order_info['buyer_id'] = buyer.id
            updated_order['buyer_info'] = jsonable_encoder(buyer_info)
        if order_info.get("product_info_list"):
            product_info_list = order_info.pop('product_info')
            updated_products = crud.product.update_product_info(db=db,product_info_list=product_info_list,user_id=user.id)
            updated_order['product_info'] = jsonable_encoder(updated_products)
        order = crud.order.update(db=db,db_obj=order_obj,obj_in=order_info)
        updated_order = { **updated_order, **jsonable_encoder(order) }
        return updated_order

    # def get_filtered_orders(self,db:Session):
    #     pass

    def get_order_info_detailed(self,db:Session,id):
        '''
        order,user,order_type,order_status,product,order_product,address,address_type,company
        select * from order
        join order_type on order_type.id = order.order_type
        join order_status on order_status.id = order.status
        join payment_type on payment_type.id = order.payment_type
        join users as u1 on u1.id = order.buyer_id
        join users as u2 on u2.id = order.users_id
        join company as c1 on c1.id = u1.company_id
        join company as c2 on c2.id = u2.company_id
        join address as a1 on a1.users_id = order.buyer_id
        join address_type as at1 on at1.id = address.type
        join address as a2 on a2.users_id = order.users_id
        join address_type as at2 on at2.id = address.type
        join order_product as op1 on op1.order_id = order.id
        join product as p1 on p1.id = order_product.product_id



        select * from order
        join order_type on order_type.id = order.order_type
        join order_status on order_status.id = order.status
        join payment_type on payment_type.id = order.payment_type

        select * from order_product
        join product on p.id = order_product.product_id
        where order_product.order_id = order_id

        select * from order
        join users on user.id = order.buyer_id
        join address on address.users_id = order.buyer_id
        join address_type on address.type = address_type.id
        join company on company.id = users.company_id
        where id = order_id

        select * from order
        join users on user.id = order.users_id
        join address on address.users_id = order.users_id
        join address_type on address.type = address_type.id
        join company on company.id = users.company_id
        where id = order_id

        :param db:
        :param order_id:
        :return:
        '''
        order_info = self.get_order_info(db=db,id=id)
        if order_info is None:
            return None
        products_info = self.get_products_by_order(db=db,id=id)
        buyer_info = self.get_buyer_info_by_order(db=db,id=id)
        user_info = self.get_user_info_by_order(db=db,id=id)
        result = {**order_info,'buyer_info':buyer_info,'user_info':user_info,'product_info':products_info}
        return result

    def get_order_info_detailed_with_discrepancy(self,db:Session,id):
        '''

        :param db:
        :param order_id:
        :return:
        '''
        order_info = self.get_order_info_with_discrepancy(db=db,id=id)
        if order_info is None:
            return None
        products_info = self.get_products_by_order(db=db,id=id)
        buyer_info = self.get_buyer_info_by_order(db=db,id=id)
        user_info = self.get_user_info_by_order(db=db,id=id)
        result = {**order_info,'buyer_info':buyer_info,'user_info':user_info,'product_info':products_info}
        return result

    def get_orders_by_status(self,db:Session,created_by,status=None):
        if status:
            orders = db.query(self.model.id).filter(self.model.status_id == status,self.model.users_id==created_by).order_by(self.model.id.desc()).all()
        else:
            orders = db.query(self.model.id).filter(self.model.status_id != 4,self.model.users_id==created_by).order_by(self.model.id.desc()).all()
        orders = list(x[0] for x in orders)
        return orders


    def get_orders_by_product(self,db:Session,product_id):
        orders = db.query(OrderProduct.order_id).filter(OrderProduct.product_id == product_id).all()
        orders = list(x[0] for x in orders)
        return orders

    def generate_order_id(self,db:Session,user_id):
        order_ids = db.query(self.model.order_id).filter(self.model.users_id == user_id).all()
        order_ids = list(x[0] for x in order_ids)
        random_order_id = None
        for i in range(constants.ORDER_ID_CREATION_RETRY):
            random_order_id = random_with_N_digits(9)
            if str(random_order_id) not in order_ids:
                break
        return random_order_id

    def check_order_id(self,db:Session, order_id, user_id) -> bool:
        return db.query(literal(True)).filter(
                   self.model.users_id == user_id,
                   self.model.order_id == order_id
               ).scalar() or False

    def get_filtered_orders(self, db: Session, filter_fields: Dict, date_from, date_to, page, per_page,
                            sort_fields=None):

        buyer = aliased(Users)
        user = aliased(Users)
        buyer_company = aliased(Company)
        user_company = aliased(Company)
        buyer_address = aliased(Address)
        user_address = aliased(Address)
        order_status_base = aliased(OrderStatus)
        db_obj = db.query(self.model,OrderStatus,OrderType,PaymentType,buyer,user,buyer_company,user_company,
                          buyer_address,user_address,order_status_base).select_from(self.model)\
            .outerjoin(OrderType,OrderType.id == self.model.order_type_id)\
            .outerjoin(OrderStatus,OrderStatus.id == self.model.status_id) \
            .outerjoin(order_status_base, order_status_base.parent_id == OrderStatus.id) \
            .outerjoin(PaymentType,PaymentType.id == self.model.payment_type_id)\
            .outerjoin(buyer,buyer.id == self.model.buyer_id)\
            .outerjoin(user,user.id == self.model.users_id)\
            .outerjoin(buyer_company,buyer_company.id == buyer.company_id)\
            .outerjoin(user_company,user_company.id == user.company_id)\
            .outerjoin(buyer_address,buyer_address.id == self.model.drop_address_id)\
            .outerjoin(user_address, user_address.id == self.model.pickup_address_id) \

        fields_dict = {
            "status_name": OrderStatus.name,
            "status": Order.status_id,
            "payment_type": Order.payment_type_id,
            "sku": Product.sku,
            "pickup_address_tag": Address.tag,
            "buyer_country": Address.country,
            "order_id": Order.order_id,
            "order_type": Order.order_type_id,
            "order_type_name": OrderType.name
        }

        filter_list = []
        if date_from:
            filter_list.append(self.model.created_date >= date_from)

        if date_to:
            filter_list.append(self.model.created_date <= date_to)

        for field, value in filter_fields.items():
            if field in fields_dict and value:
                filter_list.append(fields_dict[field] == value)

        db_obj = db_obj.filter(*filter_list)

        if sort_fields:
            order_list = []
            orders = self.get_orders(db_obj=db_obj, orders=order_list, fields_dict=fields_dict,
                                     order_list=sort_fields)
            if orders:
                db_obj = db_obj.order_by(*orders)

        db_obj = db_obj.limit(per_page).offset((page - 1) * per_page).all()

        if not db_obj:
            return []

        db_obj_list = db_obj
        global_dict = {}
        for db_obj_data in db_obj_list:
            temp_dict = {**jsonable_encoder(db_obj_data[0])}
            temp_dict['base_status_id'] = db_obj_data[10].id if db_obj_data[10] is not None else None
            temp_dict['base_status_name'] = db_obj_data[10].name if db_obj_data[10] is not None else None
            temp_dict['status_name'] = db_obj_data[1].name
            temp_dict['order_type_name'] = db_obj_data[2].name
            temp_dict['payment_type_name'] = db_obj_data[3].name
            temp_dict['buyer_info'] = {**jsonable_encoder(db_obj_data[4])}
            temp_dict['user_info'] = {**jsonable_encoder(db_obj_data[5])}
            temp_dict['buyer_info']['company_name'] = db_obj_data[6].name if db_obj_data[6] else ''
            temp_dict['buyer_info']['company_gst'] = db_obj_data[6].gst if db_obj_data[6] else ''
            temp_dict['buyer_info'].update({**jsonable_encoder(db_obj_data[8])})
            temp_dict['user_info']['company_name'] = db_obj_data[7].name if db_obj_data[7] else ""
            temp_dict['user_info']['company_gst'] = db_obj_data[7].gst if db_obj_data[7] else ""
            temp_dict['user_info'].update({**jsonable_encoder(db_obj_data[9])})
            temp_dict['product_info'] = []
            global_dict[db_obj_data[0].id] = temp_dict
            global_dict[db_obj_data[0].id]['product_info'] = self.get_products_by_order(db=db,id=db_obj_data[0].id)

        result = list(global_dict.values())
        return result

    def get_orders_with_user(order_id: int, db: Session):
        """
        Get orders with the username who created the order.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        user = db.query(User).filter(User.id == order.created_by).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        formatted_order = {
            "order_id": order.id,
            "order_details": {
                "created_at": order.created_at,
                # Add other order details as needed
            },
            "user_name": user.username
        }
        return formatted_order

    def get_filtered_discrepancy_orders(self, db: Session, filter_fields: Dict = {}, date_from=None, date_to=None, page=1, per_page=10,
                            sort_fields=None):

        buyer = aliased(Users)
        user = aliased(Users)
        buyer_company = aliased(Company)
        user_company = aliased(Company)
        buyer_address = aliased(Address)
        user_address = aliased(Address)
        order_status_base = aliased(OrderStatus)
        db_obj = db.query(self.model,OrderStatus,OrderType,PaymentType,buyer,user,buyer_company,user_company,
                          buyer_address,user_address,Product,order_status_base,WeightDiscrepancy,WeightDiscrepancyStatus.name,OrderProduct).select_from(self.model)\
            .outerjoin(OrderType,OrderType.id == self.model.order_type_id)\
            .outerjoin(OrderStatus,OrderStatus.id == self.model.status_id) \
            .outerjoin(order_status_base, order_status_base.parent_id == OrderStatus.id) \
            .outerjoin(PaymentType,PaymentType.id == self.model.payment_type_id)\
            .outerjoin(buyer,buyer.id == self.model.buyer_id)\
            .outerjoin(user,user.id == self.model.users_id) \
            .join(WeightDiscrepancy, WeightDiscrepancy.order_id == self.model.id) \
            .join(WeightDiscrepancyStatus, WeightDiscrepancyStatus.id == WeightDiscrepancy.status_id) \
            .outerjoin(buyer_company,buyer_company.id == buyer.company_id)\
            .outerjoin(user_company,user_company.id == user.company_id)\
            .outerjoin(buyer_address,buyer_address.id == self.model.drop_address_id)\
            .outerjoin(user_address, user_address.id == self.model.pickup_address_id) \
            .outerjoin(OrderProduct, OrderProduct.order_id == self.model.id)\
            .outerjoin(Product, Product.id == OrderProduct.product_id)

        fields_dict = {
            "status_name": OrderStatus.name,
            "status": Order.status_id,
            "payment_type": Order.payment_type_id,
            "sku": Product.sku,
            "pickup_address_tag": Address.tag,
            "buyer_country": Address.country,
            "order_id": Order.order_id,
            "order_type": Order.order_type_id,
            "order_type_name": OrderType.name
        }

        filter_list = [OrderStatus.name != 'cancelled']
        if date_from:
            filter_list.append(self.model.created_date >= date_from)

        if date_to:
            filter_list.append(self.model.created_date <= date_to)

        for field, value in filter_fields.items():
            if field in fields_dict and value:
                filter_list.append(fields_dict[field] == value)

        db_obj = db_obj.filter(*filter_list)

        if sort_fields:
            order_list = []
            orders = self.get_orders(db_obj=db_obj, orders=order_list, fields_dict=fields_dict,
                                     order_list=sort_fields)
            if orders:
                db_obj = db_obj.order_by(*orders)

        total_entries = len(db_obj.all())
        db_obj = db_obj.limit(per_page).offset((page - 1) * per_page).all()

        if not db_obj:
            return []

        db_obj_list = db_obj
        global_dict = {}
        for db_obj_data in db_obj_list:
            if db_obj_data[0].id not in global_dict:
                temp_dict = {**jsonable_encoder(db_obj_data[0])}
                temp_dict['base_status_id'] = db_obj_data[11].id if db_obj_data[11] is not None else None
                temp_dict['base_status_name'] = db_obj_data[11].name if db_obj_data[11] is not None else None
                temp_dict['status_name'] = db_obj_data[1].name
                temp_dict['order_type_name'] = db_obj_data[2].name
                temp_dict['payment_type_name'] = db_obj_data[3].name
                temp_dict['buyer_info'] = {**jsonable_encoder(db_obj_data[4])}
                temp_dict['user_info'] = {**jsonable_encoder(db_obj_data[5])}
                temp_dict['buyer_info']['company_name'] = db_obj_data[6].name if db_obj_data[6] else ""
                temp_dict['buyer_info']['company_gst'] = db_obj_data[6].gst if db_obj_data[6] else ""
                temp_dict['buyer_info'].update({**jsonable_encoder(db_obj_data[8])})
                temp_dict['user_info']['company_name'] = db_obj_data[7].name if db_obj_data[7] else ""
                temp_dict['user_info']['company_gst'] = db_obj_data[7].gst if db_obj_data[7] else ""
                temp_dict['user_info'].update({**jsonable_encoder(db_obj_data[9])})
                temp_dict['excess_rate'] = db_obj_data[12].excess_rate
                temp_dict['excess_weight'] = db_obj_data[12].excess_weight
                temp_dict['discrepancy_id'] = db_obj_data[12].id
                temp_dict['charged_weight'] = db_obj_data[12].charged_weight
                temp_dict['status_updated_on'] = db_obj_data[12].modified_date
                temp_dict['discrepancy_status_name'] = db_obj_data[13]
                temp_dict['product_info'] = []
                global_dict[db_obj_data[0].id] = temp_dict
                global_dict[db_obj_data[0].id]['product_info'].append({**jsonable_encoder(db_obj_data[10]),'quantity': db_obj_data[14].quantity})

        result = list(global_dict.values())
        return {'total_rows':total_entries,'data':result}
    def get_latest_partner_order(self,db: Session, partner_id):
        db_obj = db.query(self.model.waybill_no).filter(self.model.partner_id==partner_id).order_by(desc(self.model.id))
        db_obj = db_obj.first()
        return {'waybill_no': db_obj[0]}

    def get_order_details(self,db:Session,id):

        users = aliased(Users)
        user_address = aliased(Address)
        user_company = aliased(Company)
        db_obj = db.query(self.model,OrderStatus.name,OrderType.name,PaymentType.name,Partner.name,Users,Address,Company,users,user_address,user_company
              ,Product,OrderProduct.quantity,OrderProduct.unit_price).select_from(self.model).outerjoin(OrderType, OrderType.id == self.model.order_type_id) \
            .outerjoin(OrderStatus, OrderStatus.id == self.model.status_id) \
            .outerjoin(Partner, Partner.id == self.model.partner_id) \
            .outerjoin(PaymentType, PaymentType.id == self.model.payment_type_id).outerjoin(Users, Users.id == self.model.buyer_id) \
            .outerjoin(Address, Address.id == self.model.drop_address_id) \
            .outerjoin(Company, Company.id == Users.company_id).outerjoin(users, users.id == self.model.users_id) \
            .outerjoin(user_address, user_address.id == self.model.pickup_address_id) \
            .outerjoin(user_company, user_company.id == users.company_id) \
            .outerjoin(OrderProduct,OrderProduct.order_id == self.model.id) \
            .outerjoin(Product,OrderProduct.product_id == Product.id) \
            .filter(self.model.id == id).all()

        # products_info = self.get_products_by_order(db=db, id=id)

        formatted_data = []
        for row in db_obj:
            order_info = {
                **jsonable_encoder(row[0]),  # Convert order data to JSON serializable format
                "status_name": row[1],
                "order_type_name": row[2],
                "payment_type_name": row[3],
                "partner_name": row[4]
            }

            buyer_info = {
                **jsonable_encoder(row[5]),  # Convert buyer data to JSON serializable format
                **jsonable_encoder(row[6]),  # Convert drop address data to JSON serializable format
                'company_name': row[7].name if row[7] else "",
                'company_gst': row[7].gst if row[7] else ""
            }  # Convert company data to JSON serializable format

            user_info = {
                **jsonable_encoder(row[8]),  # Convert user data to JSON serializable format
                **jsonable_encoder(row[9]),  # Convert user address data to JSON serializable format
                'company_name': row[10].name if row[10] else "",
                'company_gst': row[10].gst if row[10] else ""
            }
            # Convert user company data to JSON serializable format
            products_info = {
                **jsonable_encoder(row[11]),
                'quantity': row[12] if row[12] else 0, 'unit_price': row[13] if row[13] else 0
            }

        result = {**order_info, 'buyer_info': buyer_info, 'user_info': user_info, 'product_info': [products_info]}
        return result

def get_order_status_by_id(db: Session, order_id: int) -> Optional[OrderStatus]:
    """
    Get order status by order ID.
    """
    return db.query(OrderStatus).filter(OrderStatus.id == order_id).first()




order = CRUDOrder(Order)