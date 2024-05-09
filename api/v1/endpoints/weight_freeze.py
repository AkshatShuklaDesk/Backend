from typing import Any, List,Dict, Optional, Annotated
from fastapi.encoders import jsonable_encoder
from datetime import date, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query, File
from sqlmodel import Session
import itertools
from datetime import datetime
import crud, models,schemas
from integrations.delhivery import DelhiveryClient
from scripts.utilities import get_data_from_file
from api.deps import get_db
from schemas.delhivery.shipment import CreateShipment, GetShippingCost, PickupDateTime, PickupDetail
import csv
from io import TextIOWrapper
import codecs
from copy import deepcopy
from scripts.order import create_order_info_from_file

# this is temporary till user auth flow gets implemented
from temp import test_user
from core.logging_utils import setup_logger
import logging
log_name = "weight_freeze"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()

@router.post("/")
def save_weight_freeze(
    *,
    db: Session = Depends(get_db),
    weight_freeze_in: models.WeightFreezeCreate
) -> Any:
    """
    WEight freeze request api
    """
    try:
        weight_freeze_json = jsonable_encoder(weight_freeze_in)
        logger.info(f'create api arg for in {id} :- {weight_freeze_json}')
        result = crud.weight_freeze.create_weight_freeze(db=db,obj_in=weight_freeze_json,user_id=test_user.id)
        output = {'weight_freeze_id':result.id}
        db.commit()
        return output
    except Exception as e:
        logger.error(f'Error in weight freeze save API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.put("/update")
def update_weight_freeze(
    *,
    db: Session = Depends(get_db),
    weight_freeze_in: models.WeightFreezeCreate,
    id: int
) -> Any:
    """
    WEight freeze request api
    """
    try:
        weight_freeze_in = weight_freeze_in.model_dump(exclude_unset=True)
        weight_freeze_json = jsonable_encoder(weight_freeze_in)
        logger.info(f'update api arg for in {id} :- {weight_freeze_json}')

        result = crud.weight_freeze.update_weight_freeze(db=db,obj_in=weight_freeze_json,user_id=test_user.id,id=id)
        output = {'weight_freeze_id':result.id}
        db.commit()
        return output
    except Exception as e:
        logger.error(f'Error in weight freeze update API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.get("/get_weight_freeze")
def get_weight_freeze(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 10,
    from_date: Annotated[Optional[date], Query(alias="from")] = None,
    to_date: Annotated[Optional[date], Query(alias="to")] = None,
    status_name: Optional[str] = None,
    status_id: Optional[int] = None,
    search: Optional[str] = None
) -> Any:
    """
    WEight freeze request api
    """
    try:

        result = crud.weight_freeze.get_weight_freeze_products(
            db=db,
            filter_fields=locals(),
            date_from=from_date,
            date_to=to_date,
            # sort_fields=sort_fields,
            page=page,
            per_page=per_page,
            user_id=test_user.id)
        return result
    except Exception as e:
        logger.error(f'Error in weight freeze update API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.get("/get_status_counts")
def get_weight_freeze_status_counts(
    *,
    db: Session = Depends(get_db)
) -> Any:
    """
    WEight freeze request api
    """
    try:

        result = crud.weight_freeze.get_status_wise_count(
            db=db,user_id=test_user.id)
        return result
    except Exception as e:
        logger.error(f'Error in weight freeze update API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.post("/import")
def import_weight_freeze(
    *,
    db: Session = Depends(get_db),
    file:UploadFile = File(...)
) -> Any:
    """
    WEight freeze import request api
    name,sku,length,width,height,weight,status,img1,img2,length_img,width_img,height_img,weight_img
    """
    try:
        weight_freeze_dict = get_data_from_file(file=file)
        weight_freeze_list = list(itertools.chain.from_iterable(list(weight_freeze_dict.values())))
        result = crud.weight_freeze.create_weight_freeze_from_file(db=db,obj_in=weight_freeze_list,user_id=test_user.id)
        db.commit()
        return result
    except Exception as e:
        logger.error(f'Error in weight freeze import API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')