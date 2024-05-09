from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, aliased
from sqlmodel import literal

from crud.base import CRUDBase
import crud
import constants
from models.address import Address
from models.partner import Partner
from models.returns import Returns, ReturnsCreate, ReturnsBase
from models.returns_status import ReturnsStatus
from models.returns_reason import ReturnsReason
from models.returns_product import ReturnsProduct
from models.payment_type import PaymentType
from models.product import Product
from models.users import Users
from scripts.utilities import random_with_N_digits


class CRUDReturn(CRUDBase[Returns, ReturnsCreate, ReturnsBase]):
    def get_return_info(self,db:Session,id):
        return_info = db.query(self.model, ReturnsStatus.name, ReturnsReason.name, Partner.name, PaymentType.name) \
            .select_from(self.model) \
            .outerjoin(ReturnsStatus, ReturnsStatus.id == self.model.status_id) \
            .outerjoin(ReturnsReason, ReturnsReason.id == self.model.returns_reason_id) \
            .outerjoin(Partner, Partner.id == self.model.partner_id) \
            .outerjoin(PaymentType, PaymentType.id == self.model.payment_type_id) \
            .filter(self.model.id == id).first()

        if return_info is None:
            return None
        result = {
            **jsonable_encoder(return_info[0]),
            'status_name': return_info[1],
            'return_reason': return_info[2],
            'partner_name': return_info[3],
            'payment_type_name': return_info[4],
        }
        return result

    def get_products_by_return(self,db:Session,id):
        product_info = db.query(Product,ReturnsProduct.quantity).select_from(ReturnsProduct) \
            .outerjoin(Product, ReturnsProduct.product_id == Product.id) \
            .filter(ReturnsProduct.return_id == id).all()
        result = []
        for product in product_info:
            result.append({**jsonable_encoder(product[0]),'quantity':product[1]})
        return result

    def get_buyer_info_by_return(self,db:Session,id):
        buyer_info = db.query(Users,Address).select_from(self.model)\
            .outerjoin(Users, Users.id == self.model.buyer_id)\
            .outerjoin(Address, Address.id == self.model.drop_address_id) \
            .filter(self.model.id == id).first()
        result = { **jsonable_encoder(buyer_info[0]),**jsonable_encoder(buyer_info[1]) }
        return result

    def get_user_info_by_return(self,db:Session,id):
        user_info = db.query(Users,Address).select_from(self.model)\
            .outerjoin(Users, Users.id == self.model.buyer_id)\
            .outerjoin(Address, Address.id == self.model.pickup_address_id) \
            .filter(self.model.id == id).first()
        result = {**jsonable_encoder(user_info[0]), **jsonable_encoder(user_info[1]) }
        return result

    def create_return(self,db:Session, return_in, user_id, logger=None):
        try:
            return_info = jsonable_encoder(return_in)
            exist_status = self.check_return_id(db=db, return_id=return_info['return_id'] ,user_id=user_id)
            if exist_status:
                raise ValueError(f"return_id already exists: {return_info['return_id']}")
            buyer_info = return_info['buyer_info']
            buyer = crud.users.check_and_create_user(db=db,user_in=buyer_info)
            address_info = return_info['address_info']
            address_info['users_id'] = buyer.id
            address = crud.address.create(db=db,obj_in=address_info)
            if return_info["pickup_address"].get("id") is not None:
                if not return_info["pickup_address"]["id"]:
                    raise ValueError(f"Missing location_id in order {return_info['order_id']}")
                pickup_address = crud.address.get(db=db, id=return_info["pickup_address"]["id"])
            else:
                pickup_address = crud.address.check_save_user_address(db=db, address_in=return_info['pickup_address'])
            products = crud.product.check_and_save_products(db=db,product_in=return_info['product_info'],user_id=user_id)
            return_info['users_id'] = user_id
            return_info['pickup_address_id'] = pickup_address.id
            return_info['drop_address_id'] = address.id
            return_info['status_id'] = crud.returns_status.get_by_name(db=db,name='new').id
            return_info['partner_id'] = crud.partner.get_by_name(db=db,name=return_info["partner_name"] or "Delhivery").id
            return_info['payment_type_id'] = crud.payment_type.get_by_name(db=db,
                                                                          name="prepaid").id
            return_info['returns_reason_id'] = crud.returns_reason.get_by_name(db=db,name=return_info['return_reason']).id
            return_info['buyer_id'] = buyer.id
            del return_info['buyer_info']
            del return_info['product_info']
            del return_info['pickup_address']
            del return_info['address_info']
            return_obj = self.create(db=db,obj_in=return_info)
            crud.returns_product.create_multiple_return_products(db=db, order_id=return_obj.id,products=products)
            return return_obj
        except Exception as e:
            if logger:
                logger.info(f'Exception in create order crud function : {e}')
            raise e

    def update_return(self,db:Session,return_in,id,user=None):
        if isinstance(return_in, dict):
            return_info = jsonable_encoder(return_in)
        else:
            return_info = return_in.model_dump(exclude_unset=True)

        return_obj = crud.returns.get(db=db,id=id)
        updated_return = {}
        if return_info.get("status"):
            status = return_info.pop("status")
            order_status = crud.returns_status.get_by_name(db, status)
            if not order_status:
                raise Exception(f"Invalid order status: {return_info['status']}")
            return_info['status_id'] = order_status.id
        if return_info.get("buyer_info"):
            buyer_info = return_info.pop('buyer_info')
            buyer = crud.users.update_user_info(db=db,user_in=buyer_info)
            return_info['buyer_id'] = buyer.id
            updated_return['buyer_info'] = jsonable_encoder(buyer_info)
        if return_info.get("product_info_list"):
            product_info_list = return_info.pop('product_info')
            updated_products = crud.product.update_product_info(db=db,product_info_list=product_info_list,user_id=user_id)
            updated_return['product_info'] = jsonable_encoder(updated_products)
        return_obj = crud.returns.update(db=db,db_obj=return_obj,obj_in=return_info)
        updated_return = { **updated_return, **jsonable_encoder(return_obj) }
        return updated_return

    def get_return_info_detailed(self,db:Session,id):
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
        return_info = self.get_return_info(db=db,id=id)
        if return_info is None:
            return None
        products_info = self.get_products_by_return(db=db,id=id)
        buyer_info = self.get_buyer_info_by_return(db=db,id=id)
        user_info = self.get_user_info_by_return(db=db,id=id)
        result = {**return_info,'buyer_info':buyer_info,'user_info':user_info,'product_info':products_info}
        return result

    def get_returns_by_status(self,db:Session,status=None):
        if status:
            returns = db.query(self.model.id).filter(self.model.status_id == status).all()
        else:
            returns = db.query(self.model.id).filter(self.model.status_id != 4).all()
        returns = list(x[0] for x in returns)
        return returns

    def generate_return_id(self,db:Session,user_id):
        return_ids = db.query(self.model.return_id).filter(self.model.users_id == user_id).all()
        return_ids = list(x[0] for x in return_ids)
        random_return_id = None
        for _ in range(constants.ORDER_ID_CREATION_RETRY):
            random_return_id = random_with_N_digits(9)
            if str(random_return_id) not in return_ids:
                break
        return random_return_id

    def check_return_id(self,db:Session, return_id, user_id) -> bool:
        return db.query(literal(True)).filter(
                   self.model.users_id == user_id,
                   self.model.return_id == return_id
               ).scalar() or False

    def get_filtered_returns(self, db: Session, filter_fields: dict, date_from, date_to, page, per_page,user_id,
                            sort_fields=None):
        buyer = aliased(Users)
        user = aliased(Users)
        buyer_address = aliased(Address)
        user_address = aliased(Address)
        return_status_base = aliased(ReturnsStatus)
        db_obj = db.query(self.model,ReturnsStatus,ReturnsReason,buyer,user,
                          buyer_address,user_address,return_status_base,Partner.name,PaymentType.name).select_from(self.model) \
            .outerjoin(ReturnsReason, ReturnsReason.id == self.model.returns_reason_id) \
            .outerjoin(ReturnsStatus, ReturnsStatus.id == self.model.status_id) \
            .outerjoin(return_status_base, return_status_base.parent_id == ReturnsStatus.id) \
            .outerjoin(PaymentType, PaymentType.id == self.model.payment_type_id) \
            .outerjoin(buyer,buyer.id == self.model.buyer_id) \
            .outerjoin(user,user.id == self.model.users_id) \
            .outerjoin(buyer_address,buyer_address.id == self.model.drop_address_id) \
            .outerjoin(user_address, user_address.id == self.model.pickup_address_id) \
            .outerjoin(Partner, Partner.id == self.model.partner_id).filter(Users.id == user_id)

        fields_dict = {
            "status_name": ReturnsStatus.name,
            "status": Returns.status_id,
            "sku": Product.sku,
            "pickup_address_tag": Address.tag,
            "buyer_country": Address.country,
            "return_id": Returns.return_id,
            "return_reason": Returns.returns_reason_id,
            "return_reason_name": ReturnsReason.name
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
        # result
        for db_obj_data in db_obj_list:
            # if db_obj_data[0].id not in global_dict:
            temp_dict = {**jsonable_encoder(db_obj_data[0])}
            temp_dict['base_status_id'] = db_obj_data[7].id if db_obj_data[7] is not None else None
            temp_dict['base_status_name'] = db_obj_data[7].name if db_obj_data[7] is not None else None
            temp_dict['status_name'] = db_obj_data[1].name
            temp_dict['return_reason_name'] = db_obj_data[2].name
            temp_dict['buyer_info'] = {**jsonable_encoder(db_obj_data[3])}
            temp_dict['user_info'] = {**jsonable_encoder(db_obj_data[4])}
            temp_dict['buyer_info'].update({**jsonable_encoder(db_obj_data[5])})
            temp_dict['user_info'].update({**jsonable_encoder(db_obj_data[6])})
            temp_dict['partner_name'] = db_obj_data[8]
            temp_dict['payment_type_name'] = db_obj_data[9]
            temp_dict['product_info'] = []
            global_dict[db_obj_data[0].id] = temp_dict
            global_dict[db_obj_data[0].id]['product_info'] = self.get_products_by_return(db=db,id=db_obj_data[0].id)
            # global_dict[db_obj_data[0].id]['product_info'].append({**jsonable_encoder(db_obj_data[7])})

        result = list(global_dict.values())
        return result


returns = CRUDReturn(Returns)
