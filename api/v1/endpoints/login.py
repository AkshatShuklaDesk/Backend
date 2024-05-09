from datetime import timedelta
from typing import Any,Dict
import random
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import smtplib
import crud, models, schemas
from api import deps
from core import security
# from app.core.config import settings
import constants
from core.security import get_password_hash
# from utils import (
#     generate_password_reset_token,
#     send_reset_password_email,
#     verify_password_reset_token,
# )
from passlib.hash import bcrypt

import logging

router = APIRouter()
# log_name = "login"
# endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
# logger = logging.getLogger(log_name)

@router.post("/access-token", response_model=Dict)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = crud.users.authenticate(
            db, name=form_data.username, password=form_data.password
        )
        if not user:
            return {"msg":"Incorrect mail or password"}

        elif not crud.users.is_active(user):
            raise HTTPException(status_code=400, detail="Inactive user")
        access_token_expires = timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user_id":user.id,
            "user_name":f'{user.first_name} {user.last_name}',
            "is_admin":user.is_admin,
            "is_company" : 0,
            "kyc_status_id":user.kyc_status_id,
            "user_type_id" : user.users_type_id
        }
    except Exception as e:
        raise HTTPException(status_code=401,detail="Exeption in login api")


# @router.post("/login/test-token", response_model=schemas.Users)
# def test_token(current_user: models.Users = Depends(deps.get_current_user)) -> Any:
#     """
#     Test access token
#     """
#     return current_user


# @router.post("/password-recovery/{email}", response_model=schemas.Msg)
# def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
#     """
#     Password Recovery
#     """
#     user = crud.user.get_by_email(db, email=email)
#
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     password_reset_token = generate_password_reset_token(email=email)
#     send_reset_password_email(
#         email_to=user.email, email=email, token=password_reset_token
#     )
#     return {"msg": "Password recovery email sent"}


# @router.post("/reset-password/", response_model=schemas.Msg)
# def reset_password(
#     token: str = Body(...),
#     new_password: str = Body(...),
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Reset password
#     """
#     email = verify_password_reset_token(token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid token")
#     user = crud.user.get_by_email(db, email=email)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     elif not crud.user.is_active(user):
#         raise HTTPException(status_code=400, detail="Inactive user")
#     # hashed_password = get_password_hash(new_password)
#     hashed_password = (new_password)
#     user.password = hashed_password
#     db.add(user)
#     db.commit()
#     return {"msg": "Password updated successfully"}

@router.post("/generate_otp")
def generate_otp(*, db: Session = Depends(deps.get_db), email_id :str, user_id) -> Any:
    
    try:
        db_obj = crud.users_auth.set_otp_for_user_id(db=db,user_id=user_id,email_id=email_id)
        return db_obj
    except Exception as e:
        print(f'Error in Generating OTP api : {e}')
        raise HTTPException(status_code=401,detail="Exception in Generating OTP api")

@router.get("/verify_otp")
def verify_otp(*, db: Session = Depends(deps.get_db), otp, user_id):
    try:
        last_otp = crud.users_auth.verify_otp(db=db,otp=otp,user_id=user_id)
        if last_otp == 1:
            return {"flag" : 1 , "msg" : "otp verfied"}
        elif last_otp == 0:
            return {"flag" : 0 , "msg" : "otp mismatch"}
        else:
            return {"flag" : 2 , "msg" : "User not found"}
    except Exception as e:
        print(f'Error in Generating OTP api : {e}')
        raise HTTPException(status_code=401,detail="Exception in Generating OTP api")
    


        

