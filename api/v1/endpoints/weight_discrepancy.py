from typing import Any, List,Dict, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from datetime import datetime
import itertools
import crud, models,schemas
from integrations.delhivery import DelhiveryClient
from api.deps import get_db
import io
from scripts.utilities import get_data_from_file
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
log_name = "weight_discrepancy"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()

@router.post("/")
def save_weight_discrepancy(
    *,
    db: Session = Depends(get_db),
    weight_discrepancy_in: models.WeightDiscrepancyCreate
) -> Any:
    """
    WEight discrepancy request api
    """
    try:
        weight_discrepancy_json = jsonable_encoder(weight_discrepancy_in)
        result = crud.weight_discrepancy.create_weight_discrepancy(db=db,obj_in=weight_discrepancy_json,user_id=test_user.id)
        output = {'weight_discrepancy_id':result.id}
        db.commit()
        return output
    except Exception as e:
        logger.error(f'Error in weight discrepancy save API :- {e}')
        raise HTTPException(status_code=401,detail=f'error : {e}')

@router.post("/import")
def import_weight_discrepancy(
    *,
    db: Session = Depends(get_db),
    file:UploadFile = File(...)
) -> Any:
    """
    WEight discrepancy request api
    """
    try:
        weight_discrepancy_dict = get_data_from_file(file=file)
        weight_discrepancy_list = list(itertools.chain.from_iterable(list(weight_discrepancy_dict.values())))
        result = crud.weight_discrepancy.create_weight_discrepancy(db=db,obj_in=weight_discrepancy_list,user_id=test_user.id)
        db.commit()
        print(weight_discrepancy_dict)
        return result
    except Exception as e:
        logger.error(f'Error in weight discrepancy save API :- {e}')
        raise HTTPException(status_code=401,detail=f'error : {e}')

@router.put("/update")
def update_weight_discrepancy(
    *,
    db: Session = Depends(get_db),
    weight_discrepancy_in: models.WeightDiscrepancyCreate,
    id: int
) -> Any:
    """
    WEight discrepancy request api
    """
    try:
        weight_discrepancy_in = weight_discrepancy_in.model_dump(exclude_unset=True)
        weight_discrepancy_json = jsonable_encoder(weight_discrepancy_in)

        logger.info(f' Weight discr update api args : {weight_discrepancy_json}')
        result = crud.weight_discrepancy.update_weight_discrepancy(db=db,obj_in=weight_discrepancy_json,user_id=test_user.id,id=id)
        output = {'weight_discrepancy_id':result.id}
        db.commit()
        return output
    except Exception as e:
        logger.error(f'Error in weight discrepancy update API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.put("/dispute")
def update_weight_discrepancy_dispute(
    *,
    db: Session = Depends(get_db),
    weight_discrepancy_in: models.WeightDiscrepancyDispute,
    id: int
) -> Any:
    """
    WEight discrepancy request api
    """
    try:
        weight_discrepancy_in = weight_discrepancy_in.model_dump(exclude_unset=True)
        weight_discrepancy_json = jsonable_encoder(weight_discrepancy_in)

        result = crud.weight_discrepancy.update_weight_discrepancy_dispute(db=db,obj_in=weight_discrepancy_json,user_id=test_user.id,id=id)
        output = {'weight_discrepancy_product_id':result.id}
        db.commit()
        return output
    except Exception as e:
        logger.error(f'Error in weight discrepancy update API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.get("/get_weight_discrepancy")
def get_weight_discrepancy(
    *,
    db: Session = Depends(get_db)
) -> Any:
    """
    WEight discrepancy request api
    """
    try:

        result = crud.weight_discrepancy.get_weight_discrepancy_filtered(db=db,user_id=test_user.id)
        return result
    except Exception as e:
        logger.error(f'Error in weight discrepancy update API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')