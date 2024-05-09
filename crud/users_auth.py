from typing import List
import random
from sqlalchemy import update
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import smtplib
import constants
from crud.base import CRUDBase
from models.users_auth import UsersAuth, UsersAuthCreate, UsersAuthBase
from email.message import EmailMessage
from passlib.hash import bcrypt

class CRUDUsersAuth(CRUDBase[UsersAuth, UsersAuthCreate, UsersAuthBase]):
    def set_otp_for_user_id(self,db: Session , user_id ,email_id): 
        otp = random.randint(100000,999999)
        db_obj = db.query(self.model).filter(self.model.users_id == user_id).first()
        db_obj = jsonable_encoder(db_obj)
        db_obj['last_otp'] = otp
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

        final_db_obj = update(self.model).filter(self.model.users_id == user_id).values(last_otp = otp)
        db.execute(final_db_obj)
        db.commit()
        return "Success"
        
    def verify_otp(self,db:Session, otp , user_id):
        db_obj = db.query(self.model).filter(self.model.users_id == user_id).first()
        db_obj = jsonable_encoder(db_obj)

        if db_obj:
            if db_obj['last_otp'] == int(otp):
                return 1
            else:
                return 0
        else:
            return "User not found"
        
    def update_password(self, db: Session, user_id: int, new_password: str):
            print(new_password)
            if bcrypt.verify("aaravshah", new_password):
                print("Done")
            user = db.query(self.model).filter(self.model.users_id == user_id).first()
            if user:
                user.password = new_password
                db.commit()
                return True
            return False       


        



users_auth = CRUDUsersAuth(UsersAuth)
