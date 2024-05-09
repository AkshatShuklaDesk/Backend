from datetime import timedelta
from typing import Any, List

from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

import constants
import crud, models
from api import deps
from api.deps import get_db
import logging

from core import security
from core.logging_utils import setup_logger
from schemas.company import CompanyCreate
# from crud.company_auth import *

log_name = "company"
endpoint_device_logger_setup = setup_logger(log_name, level="INFO")
logger = logging.getLogger(log_name)

router = APIRouter()


@router.post("/signup")
def create_company(
        *,
        db: Session = Depends(deps.get_db),
        company_in: CompanyCreate,
) -> Any:
    """
    Create new company.
    """
    try:
        company_in = jsonable_encoder(company_in)
        company = crud.company.signup_company(db=db, comp_in=company_in)
        db.commit()
        return company
    except Exception as e:
        logger.exception(f"{e}")
        raise HTTPException(status_code=401,detail=f"{e}")



# @router.put("/{id}", response_model=models.company)
# def update_company(
#         *, db: Session = Depends(deps.get_db), id: int, company_in: CompanyCreate
# ) -> Any:
#     """
#     Update User.
#     """
#     company = crud.company.get(db=db, id=id)
#     if not company:
#         raise HTTPException(status_code=404, detail="company not found")
#     company = crud.company.update(db=db, db_obj=company, obj_in=company_in)
#     return company


#
#
# @router.get("/{id}", response_model=models.company)
# def read_company(*, db: Session = Depends(deps.get_db), id: int) -> Any:
#     """
#     Get item by ID.
#     """
#     company = crud.company.get(db=db, id=id)
#     if not company:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return company


# @router.delete("/{id}", response_model=models.company)
# def delete_company(
#         *,
#         db: Session = Depends(deps.get_db),
#         id: int,
# ) -> Any:
#     """
#     Delete an item.
#     """
#     company = crud.company.get(db=db, id=id)
#     if not company:
#         raise HTTPException(status_code=404, detail="Item not found")
#     company = crud.company.remove(db=db, id=id)
#     return company


# @router.post("/signup")
# def signup_company(
#         *,
#         db: Session = Depends(deps.get_db),
#         company_in: CompanyCreate,
# ) -> Any:
#     """
#     Create new user.
#     """
#     try:
#         company = crud.company.
#         company = jsonable_encoder(company)
#         db.commit()
#         return company
#     except Exception as e:
#         print(f'error in user signup {e}')
#         raise e


@router.post("/forget_password_otp")
def forget_password(
    *,
    db: Session = Depends(deps.get_db),
    email:str,
) -> Any:

    try:
        company=crud.company.get_company_auth_from_email(db=db,email=email)
        company=jsonable_encoder(company)
        company_id=company["id"]
        if company:
            try:
                db_obj = crud.company.set_otp_for_company_id(db=db,id=company_id,email_id=email)
                return {"status": db_obj,"comp_id":company_id}
            except Exception as e:
                print(f'Error in Generating OTP api : {e}')
                raise HTTPException(status_code=401,detail="Exception in Generating OTP api")
    except Exception as e:
        print(f'error in user signup {e}')
        raise e

@router.post("/update_password")
def update_password(new_password: dict, db: Session = Depends(deps.get_db)):
    try:
        email = new_password.get("email")
        password = new_password.get("password")

        if email is None or password is None:
            return {"error": "Email or password missing in request body"}

        company=crud.company.get_company_auth_from_email(db=db,email=email)
        if company:
            company=jsonable_encoder(company)

            print(password)
            hashed_password = bcrypt.hash(password)
            crud.company.update_password(db=db, id=company["id"], new_password=hashed_password)
            return {"message": "Password updated successfully"}
        else:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
#
@router.get("/verify_otp/")
def verify_otp(*, otp: int, id: int, db: Session = Depends(deps.get_db)):
    try:
        last_otp = crud.company.verify_otp(db=db, otp=otp, id=id)
        if last_otp == 1:
            return {"flag": 1, "msg": "otp verfied"}
        elif last_otp == 0:
            return {"flag": 0, "msg": "otp mismatch"}
        else:
            return {"flag": 2, "msg": "User not found"}
    except Exception as e:
        print(f'Error in Generating OTP api : {e}')
        raise HTTPException(status_code=401, detail="Exception in Generating OTP api")

@router.get("/{id}", response_model=models.Company)
def read_company(*, db: Session = Depends(deps.get_db), id: int) -> Any:
    """
    Get item by ID.
    """
    company = crud.company.get(db=db, id=id)
    company=jsonable_encoder(company)
    if not company:
        raise HTTPException(status_code=404, detail="Item not found")
    return company

@router.post("/access-token")
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        if form_data.username is None:
            return {"msg":"Please Enter Username"}
        if form_data.password is None:
            return {"msg":"Please Enter Password"}

        company = crud.company.authenticate(
            db, name=form_data.username, password=form_data.password
        )
        

        if not company:
            return {"msg":"Incorrect mail or password"}
        access_token_expires = timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                company.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "company_id":company.id,
            "user_name":f'{company.name}',
            "is_admin":company.is_admin,
            "is_company" : 1,
            "wallet_balance":company.wallet_balance,
            "kyc_status_id":company.kyc_status_id,
            "users_type_id" : company.users_type_id
        }
    except Exception as e:
        raise HTTPException(status_code=401,detail="Exeption in login api")


@router.post("/generate_otp")
def generate_otp(*, db: Session = Depends(deps.get_db), email_id: str, user_id) -> Any:
    try:
        db_obj = crud.company.set_otp_for_company_id(db=db, id=user_id, email_id=email_id)
        return db_obj
    except Exception as e:
        print(f'Error in Generating OTP api : {e}')
        raise HTTPException(status_code=401, detail="Exception in Generating OTP api")

@router.get("/get_company_users/")
def get_company_users(*, db:Session = Depends(deps.get_db), companyId:int) -> Any:
    try:
        db_obj = crud.company.get_company_users(db=db,companyId=companyId)
        return db_obj
    except Exception as e:
        print(f'Error in Getting users api : {e}')
        raise HTTPException(status_code=401, detail="Exception in getting users api")
    
@router.post("/update_wallet_balance")
def update_wallet_balance(*, db:Session = Depends(deps.get_db), companyId:int, user_id:int, amount:int) -> Any:
    try:
        comp_obj = crud.company.get(db=db,id=companyId)
        user_obj = crud.users.get(db=db,id=user_id)
        if amount <= comp_obj.wallet_balance:
            comp_obj.wallet_balance=comp_obj.wallet_balance-amount
            user_obj.wallet_balance=user_obj.wallet_balance+amount
            if user_obj.requested_balance <= amount:
                user_obj.requested_balance=0
                comp_balance=comp_obj.wallet_balance
                user_balance=user_obj.wallet_balance
                request_balance=user_obj.requested_balance
            else:
                user_obj.requested_balance=user_obj.requested_balance-amount
                comp_balance=comp_obj.wallet_balance
                user_balance=user_obj.wallet_balance
                request_balance=user_obj.requested_balance
            
            db.commit()
            return {"company_balace":comp_balance,"user_balance":user_balance,"request_balance":request_balance}
        else:
            return {"message":"Insufficient Balance"}
    except Exception as e:
        print(f'Error in Generating OTP api : {e}')
        raise HTTPException(status_code=401, detail="Exception in Generating OTP api") 
    
@router.post("/request_balance/")
def request_balance(*, db:Session = Depends(deps.get_db), user_id:int, amount:float) -> Any:
    try:
        
        user_obj = crud.users.get(db=db,id=user_id)
        user_obj.requested_balance=amount
        
        db.commit()
        return {"success":True}
    except Exception as e:
        print(f'Error in requesting amount : {e}')
        raise HTTPException(status_code=401, detail="Error in requesting amount ")

@router.get("/get_all_companies/")
def get_all_companies(
        *,
        db : Session = Depends(get_db)
):
    try:
        companies = crud.company.get_all_companies(db=db)
        return companies
    except Exception as e:
        print(f'Error in Getting users api : {e}')
        raise HTTPException(status_code=401, detail="Exception in getting users api")

