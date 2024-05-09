from typing import Any, List
from passlib.hash import bcrypt
from fastapi import APIRouter, Depends, HTTPException,status

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import crud, models
from api import deps
from api.deps import get_db
import logging
from core.logging_utils import setup_logger
from models.users import Users, UsersCreate, UsersBase
from crud.users_auth import *


log_name = "order"
endpoint_device_logger_setup = setup_logger(log_name, level="INFO")
logger = logging.getLogger(log_name)


router = APIRouter()


@router.post("/")
def create_users(
    *,
    db: Session = Depends(deps.get_db),
    users_in: models.UsersCreate,
) -> Any:
    """
    Create new user.
    """
    users = crud.users.create(db=db, obj_in=users_in)
    db.commit()
    return users

@router.put("/{id}", response_model=models.Users)
def update_users(
    *, db: Session = Depends(deps.get_db), id: int, users_in: models.UsersUpdate
) -> Any:
    """
    Update User.
    """
    users = crud.users.get(db=db, id=id)
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    users = crud.users.update(db=db, db_obj=users, obj_in=users_in)
    return users


#
#
@router.get("/{id}", response_model=models.Users)
def read_users(*, db: Session = Depends(deps.get_db), id: int) -> Any:
    """
    Get item by ID.
    """
    users = crud.users.get(db=db, id=id)
    if not users:
        raise HTTPException(status_code=404, detail="Item not found")
    return users


@router.delete("/{id}", response_model=models.Users)
def delete_users(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Delete an item.
    """
    users = crud.users.get(db=db, id=id)
    if not users:
        raise HTTPException(status_code=404, detail="Item not found")
    users = crud.users.remove(db=db, id=id)
    return users

@router.post("/signup")
def signup_users(
    *,
    db: Session = Depends(deps.get_db),
    users_in: models.UsersCreate,
) -> Any:
    """
    Create new user.
    """
    try:
        users = crud.users.signup_user(db=db, user_in=users_in)
        users = jsonable_encoder(users)
        db.commit()
        return users
    except Exception as e:
        print(f'error in user signup {e}')
        raise e

# @router.post("/forget_password")
# def forget_password(
#     *,
#     db: Session = Depends(deps.get_db),
#     email:str,
# ) -> Any:
   
#     try:
#         user=crud.users.get_user_auth_from_email(db=db,email=email)
#         user_id=user["user_id"]
#         if user:
#             try:
#                 db_obj = crud.users_auth.set_otp_for_user_id(db=db,user_id=user_id,email_id=email)
#                 return db_obj
#             except Exception as e:
#                 print(f'Error in Generating OTP api : {e}')
#                 raise HTTPException(status_code=401,detail="Exception in Generating OTP api")
#     except Exception as e:
#         print(f'error in user signup {e}')
#         raise e

@router.post("/update_password")
def update_password(new_password: dict, db: Session = Depends(deps.get_db)) :
    try:
        email = new_password.get("email")
        password = new_password.get("password")

        if email is None or password is None:
            return {"error": "Email or password missing in request body"}

        user_dicts = []
        results = db.query(Users, UsersAuth).\
            select_from(Users).\
            join(UsersAuth, Users.id == UsersAuth.users_id).\
            filter(Users.email_address == email).\
            all()

        for user, user_auth in results:
            user_dict = {
                "user": user.__dict__,
                "user_auth": user_auth.__dict__
            }
            user_dicts.append(user_dict)
        if user_dict:
            print(password)
            hashed_password = bcrypt.hash(password)
            # Update the password in the database
            crud.users_auth.update_password(db=db, user_id=user_dicts[0]["user"]["id"], new_password=hashed_password)
            return {"message": "Password updated successfully"}
        else:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}
    

@router.post("/generate_otp")
def generate_otp(*, db: Session = Depends(deps.get_db), email_id :str) -> Any:
    
    try:
        user_id = db.query(Users.id).\
            select_from(Users).\
            join(UsersAuth, Users.id == UsersAuth.users_id).\
            filter(Users.email_address == email_id).\
            all()

        if user_id:
            user_id = user_id[0] 
            db_obj = crud.users_auth.set_otp_for_user_id(db=db,user_id=user_id[0],email_id=email_id)

            return {"status":db_obj,"user_id":user_id[0]}
    except Exception as e:
        print(f'Error in Generating OTP api : {e}')
        raise HTTPException(status_code=401,detail="Exception in Generating OTP api")

@router.get("/verify_forgot_pass_otp/")
def verify_otp(*, otp:int, user_id:int, db: Session = Depends(deps.get_db)):
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