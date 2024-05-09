from typing import Any, List,Dict
from city_mapping import cities,cities_swapped
from fastapi import APIRouter, Depends, HTTPException,FastAPI , File,UploadFile
from sqlalchemy.orm import Session
import pandas as pd
import constants
import os
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session
from crud import indent
import datetime
from api.deps import get_db
import crud
from db.session import SessionLocal
from auto_mailing import generate_excel_file,send_mail
from core.logging_utils import setup_logger
import logging
router = APIRouter()

log_name = "indent"
endpoint_device_logger_setup = setup_logger(log_name, level="INFO")
logger = logging.getLogger(log_name)

@router.post('/create_indent')
def create_indent(indent: dict,db:Session=Depends(get_db)):
    try:
        db_obj = crud.Indent.create_indent(db,indent)
        db_obj = jsonable_encoder(db_obj)
        db_obj['source_id'] = cities[str(db_obj['source_id'])]
        db_obj['destination_id'] = cities[str(db_obj['destination_id'])]

        keys_without_id = [key.replace('_id', '').replace('_', ' ') if '_id' in key else key for key in db_obj.keys()]
        final_dict = dict(zip(keys_without_id, list(db_obj.values())))
        for mail in constants.mail_list:
            send_mail(data=[final_dict],receiver_mail=mail,cc="",mode="Indent Report",file="indentcreation")
        db.commit()
        return db_obj
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500, detail=f"{e}")

@router.get("/get_indents")
def get_indents(*, db:Session = Depends(get_db), created_by):
    try:
        indents = crud.Indent.get_indents(db=db,created_by=created_by)
        for indent in indents:
            indent['source_id'] = cities[str(indent['source_id'])]
            indent['destination_id'] = cities[str(indent['destination_id'])]
        return indents
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500, detail=f"{e}")

@router.get("/get_indents_by_id")
def get_indents(*, db:Session = Depends(get_db), id):
    try:
        indents = crud.Indent.get(db=db,id=id)
        indents = jsonable_encoder(indents)
        indents['source_id'] = cities[str(indents['source_id'])]
        indents['destination_id'] = cities[str(indents['destination_id'])]
        print(indents)
        return indents
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500,detail=f"{e}")

@router.post("/create_bulk_indent")
async def create_bulk_indent(*,db :Session = Depends(get_db), excel_file : UploadFile = File(...)):
    try:
        os.makedirs(constants.UPLOAD_EXCEL_DIR, exist_ok=True)
        file_path = os.path.join(constants.UPLOAD_EXCEL_DIR, excel_file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await excel_file.read())

        df = pd.read_excel(file_path)

        indent_list = []
        for i in range(len(df)):
            indent = df.iloc[i]
            row_dict = indent.to_dict()
            row_dict['source_id']=row_dict['source_id'].lower()
            row_dict['destination_id']=row_dict['destination_id'].lower()
            row_dict['source_id'] = int(cities_swapped[row_dict['source_id']])
            row_dict['destination_id'] = int(cities_swapped[row_dict['destination_id']])
            indent_list.append(row_dict)

        db_obj = crud.Indent.create_mutliple(db=db,indents=indent_list)
        for mail in constants.mail_list:
            send_mail(data=indent_list, receiver_mail=mail, cc="",mode="Indent Report",file="indentcreation")
        db.commit()
        os.remove(file_path)
        return indent_list
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500, detail=f"{e}")


@router.put("/modify_indent")
def modify_indent(*,db:Session = Depends(get_db),indent:dict):
    try:
        id = indent["id"]
        check_indent = crud.Indent.get(db=db,id=id)
        if not check_indent:
            return HTTPException(status_code=401,detail=f"Indent not found with id {id}")
        update_obj = crud.Indent.update_indent(db=db,indent_info=check_indent,indent_in=indent)
        db.commit()
        return  jsonable_encoder(update_obj)

    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/get_users")
def get_users(*,db:Session=Depends(get_db)):
    try:
        users = crud.users.get_all_users(db=db)
        
        return users
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500, detail=f"{e}")
    
@router.post("/booking_confirmation")
def booking_confirmation(*,db:Session=Depends(get_db),status:dict):
    try:
        response = crud.Indent.set_confirmation(db=db,status=status)
        if response:
            crud.account_transaction.indent_approval(db=db,indent_obj=response)
            db.commit()
            return {"status":True}
        else:
            return {"status":False}
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=401, detail=f"{e.detail}")
    
@router.post("/admin_price")
def update_admin_price(*,db:Session=Depends(get_db),price:dict):
    try:
        response = crud.Indent.set_admin_price(db=db,price=price)
        if response:
            db.commit()
            return {"status":True}
        else:
            return {"status":False}
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500, detail=f"{e}")

