from typing import List,Dict
from passlib.hash import bcrypt

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.orm import class_mapper
from collections import Counter
from crud.base import CRUDBase
from models.users_auth import UsersAuth
import crud
from models.partner import Partner,PartnerBase,PartnerCreate,PartnerUpdate
from models.users import Users, UsersCreate, UsersBase
from models.indent import *
from core.security import get_password_hash,verify_password
from models.users_auth import *
from models.company import Company,CompanyBase,CompanyCreate,CompanyUpdate
from models.order import Order,OrderBase,OrderCreate,OrderUpdate
class CRUDUsers(CRUDBase[Users, UsersCreate, UsersBase]):
    def get_user_from_contact_no(self,db:Session,contact_no):
        user = db.query(self.model).filter(self.model.contact_no==contact_no).first()
        return user

    def get_user_from_email(self,db:Session,email):
        user = db.query(self.model).filter(self.model.email_address==email).first()
        return user
    
    def get_user_auth_from_email(self,db:Session,email):
        user = db.query(Users,UsersAuth).select_from(Users).join(UsersAuth,Users.id == UsersAuth.users_id).filter(self.model.email_address==email).first()
        return user
    
    def get_orders_count_by_company_id(self,db:Session,start_date,end_date,company_id):

        orders_count = db.query(Users,Order).select_from(Order).join(Users,Order.users_id == Users.id).filter(self.model.company_id==company_id,func.DATE(Order.modified_date) >= start_date,
                        func.DATE(Order.modified_date) < end_date).count()
        return orders_count

    def get_orders_details_by_company_id(self,db:Session,start_date,end_date,company_id):
        result = db.query(func.count(Order.status_id),Order.status_id).select_from(Order).join(Users,Order.users_id == Users.id).filter(self.model.company_id==company_id,func.DATE(Order.modified_date) >= start_date,
                        func.DATE(Order.modified_date) <= end_date).group_by(Order.status_id).all()
        status_counts={
            "1":0,
            "2":0,
            "3":0,
            "4":0,
            "5":0,
            "6":0,
            "7":0,
            "8":0
        }
        for count,status_id in result:
            status_counts[status_id]=count



        return status_counts
    
    def get_shipment_details(self,db:Session,start_date,end_date,company_id):
        result = db.query(
            func.count(Order.status_id),
            Order.status_id,
            Partner.name
        ).select_from(Order).join(
            Partner, Order.partner_id == Partner.id
        ).join(Users, Order.users_id == Users.id).filter(
            self.model.company_id == company_id,
            func.DATE(Order.modified_date) >= start_date,
            func.DATE(Order.modified_date) <= end_date
        ).group_by(
            Order.partner_id,Order.status_id,Partner.name
        ).all()
        
        shipment_details=[]
        for status_count,status_id,partner_name in result:
            data={}
            data["status_count"]=status_count
            data["status_id"]=status_id
            data["partner_name"]=partner_name
            shipment_details.append(data)



        return shipment_details

    def signup_user(self,db:Session,user_in):
        user_in = jsonable_encoder(user_in)
        # if user_in['contact_no']:
        #     user = self.get_user_from_contact_no(db=db, contact_no=user_in['contact_no'])
        #     if user:
        #         return {'msg':'User already exits'}
        if user_in['email_address']:
            user = self.get_user_auth_from_email(db=db, email=user_in['email_address'])
            if user:
                return {'msg':'User already exits'}
        password = user_in.pop('password')
        password = bcrypt.hash(password)
        print("This is user.password now -> ",password, user)

        user = self.create(db=db,obj_in=user_in)
        crud.users_auth.create(db=db,obj_in={'users_id':user.id,'password':password})
        return user

    def check_and_create_user(self,db:Session,user_in:Dict):
        user = self.get_user_from_contact_no(db=db,contact_no=user_in['contact_no'])
        if user:
            user_payload = {}
            for key, value in user_in.items():
                if value is None:
                    continue
                user_payload[key] = value
            user = self.update(db, db_obj=user, obj_in=user_payload)
            return user
        user = self.create(db=db,obj_in=user_in)
        return user

    def update_user_info(self,db:Session,user_in):
        user_obj = self.get(db=db,id=user_in['id'])
        user = self.update(db=db,db_obj=user_obj,obj_in=user_in)
        return user

    def is_active(self, user: Users) -> bool:
        return user.is_active

    def get_user_password(self, db: Session, users_id):
        
        user_obj = db.query(UsersAuth).filter(UsersAuth.users_id == users_id).first()
        if user_obj is None:
            return user_obj
            
        return user_obj.password

    def authenticate(self, db: Session, *, name: str, password: str):
        if '@' in name:
            user = self.get_user_from_email(db=db,email=name)
        else:
            user = self.get_user_from_contact_no(db=db,contact_no=name)

        user_password = self.get_user_password(db=db,users_id=user.id)
        if not user or not user_password:
            return None
        if bcrypt.verify(password, user_password):
            return user
       
        return None

    def update_amount(self,db:Session,id, amount,action):
        new = self.get(db=db,id=id).wallet_balance
        if action == 'minus':
            new = new - amount
        elif action == 'plus':
            new = new + amount
        else:
            new = new
        user_obj = self.update_user_info(db=db,user_in={'id':id,'wallet_balance':new})
        return user_obj
    
    def get_all_users(self,db:Session):
        users=db.query(self.model).select_from(self.model).join(Indent,self.model.id == Indent.created_by).all()
        return jsonable_encoder(users)



users = CRUDUsers(Users)
