from typing import Any, List,Dict, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session
from datetime import datetime
import crud, models,schemas
from integrations.delhivery import DelhiveryClient
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
log_name = "order_status"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()

@router.get("/get_all_base_status")
def get_all_base_status(
    *,
    db: Session = Depends(get_db)
) -> Any:
    """
    This is temporary api with static status value
    """
    try:
        result = crud.order_status.get_base_status(db=db)
        return result
    except Exception as e:
        logger.error(f'Error in order save API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')