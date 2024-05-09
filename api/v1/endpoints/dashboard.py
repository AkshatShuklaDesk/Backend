from datetime import timedelta
from typing import Any, List
from collections import Counter
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
import datetime

from core import security
from core.logging_utils import setup_logger
from schemas.company import CompanyCreate


log_name = "dashboard"
endpoint_device_logger_setup = setup_logger(log_name, level="INFO")
logger = logging.getLogger(log_name)

router = APIRouter()

@router.post("/order_analysis/")
def order_analysis(*, company_id: int, start_date:str, end_date:str, db: Session = Depends(deps.get_db)):
    try:

        current_date = datetime.datetime.now()
        next_date = current_date + datetime.timedelta(days=1)
        yesterday_date=current_date + datetime.timedelta(days=-1)
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        next_date = next_date.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_date = yesterday_date.replace(hour=0, minute=0, second=0, microsecond=0)
        todays_count = crud.users.get_orders_count_by_company_id(db=db,start_date=current_date,end_date=next_date,company_id=company_id)
        yesterdays_count=crud.users.get_orders_count_by_company_id(db=db,start_date=yesterday_date,end_date=current_date,company_id=company_id)

        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        order_details=crud.users.get_orders_details_by_company_id(db=db,start_date=start_date,end_date=end_date,company_id=company_id)

        shipment_details=crud.users.get_shipment_details(db=db,start_date=start_date,end_date=end_date,company_id=company_id)


        return {"todays_order_count":todays_count,"yesterdays_order_count":yesterdays_count,"order_details":order_details,"shipment_details":shipment_details}
    except Exception as e:
        print(f'Error in order analysis : {e}')
        raise HTTPException(status_code=401, detail="Error in order analysis")