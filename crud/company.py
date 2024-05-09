import smtplib
from email.message import EmailMessage
import random
from typing import List,Dict
from sqlalchemy import update
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from models.users import Users
import constants
from crud.base import CRUDBase
from models.company import Company, CompanyCreate, CompanyBase


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyBase]):
    def get_company_from_name(self,db:Session,name):
        company = db.query(self.model).filter(self.model.name == name).first()
        return company

    def check_and_create_company(self,db:Session,company_in:Dict):
        company = self.get_company_from_name(db=db,name=company_in['name'])
        if company:
            return company
        company = self.create(db=db,obj_in=company_in)
        return company
    
    def signup_company(self,db:Session,comp_in):
        comp_in= jsonable_encoder(comp_in)
        # if comp_in['contact_no']:
        #     user = self.get_user_from_contact_no(db=db, contact_no=comp_in['contact_no'])
        #     if user:
        #         return {'msg':'User already exits'}
        if comp_in['email']:
            company = self.get_company_auth_from_email(db=db, email=comp_in['email'])
            if company:
                return {'msg':'Company already exits'}
        password = comp_in['password']
        password = bcrypt.hash(password)
        comp_in['password'] = password
        company = self.create(db=db,obj_in=comp_in)
        return company

    def get_company_auth_from_email(self,db:Session,email):
        company = db.query(self.model).filter(self.model.email == email).first()
        return company

    def authenticate(self, db: Session, *, name: str, password: str):
        if '@' in name:
            company = self.get_company_auth_from_email(db=db, email=name)
        else:
            company = self.get_company_from_contact_no(db=db, contact_no=name)

        if not company:
            return None
        else:
            user_password = self.get_company_password(db=db, id=company.id)

        # if not verify_password(password, user.password):
        if bcrypt.verify(password, user_password):
            return company
        # if verify_password(password, user_password):
        #     return user
        return None
    def get_company_from_contact_no(self,db:Session,contact_no):
        user = db.query(self.model).filter(self.model.contact==contact_no).first()
        return user

    def get_company_password(self, db: Session, id):
        user_obj = db.query(self.model).filter(self.model.id == id).first()
        return user_obj.password

    def set_otp_for_company_id(self,db: Session , id ,email_id):
        otp = random.randint(100000,999999)
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        db_obj = jsonable_encoder(db_obj)
        db_obj['otp'] = otp
        sender_email = constants.EMAIL_ID
        password = constants.EMAIL_PASSWORD
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()

        server.login(sender_email,password=password)
        to_mail = email_id

        msg = EmailMessage()
        msg['Subject'] = "OTP Verification"
        msg['From'] = sender_email
        msg['To'] = to_mail
        msg.set_content(f"Your OTP for login is {otp}")

        server.send_message(msg=msg)
        print("Email Sent")

        final_db_obj = update(self.model).filter(self.model.id == id).values(otp= otp)
        db.execute(final_db_obj)
        db.commit()
        return "Success"
    
    def verify_otp(self,db:Session, otp , id):
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        db_obj = jsonable_encoder(db_obj)

        if db_obj:
            if db_obj['otp'] == int(otp):
                return 1
            else:
                return 0
        else:
            return "User not found"
        
    def update_password(self, db: Session, id: int, new_password: str):
        print(new_password)
        
        company = db.query(self.model).filter(self.model.id == id).first()
        if company:
            company.password = new_password
            db.commit()
            return True
        return False

    def get_company_users(self,db:Session,companyId):
        users = db.query(Users).filter(Users.company_id == companyId).all()
        users = jsonable_encoder(users)
        return users

    def get_all_companies(self,db:Session):
        companies = db.query(self.model).all()
        companies = jsonable_encoder(companies)
        return companies

company = CRUDCompany(Company)
