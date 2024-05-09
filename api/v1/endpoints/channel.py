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

log_name = "channel"
endpoint_device_logger_setup = setup_logger(log_name, level="INFO")
logger = logging.getLogger(log_name)

router = APIRouter()

@router.get("/get_channel_suggestions")
def get_channel_suggestions(
        *,
        db :Session = Depends(get_db)
):
    try:
        channels = crud.channel.get_all_channels(db=db)
        return channels
    except Exception as e:
        logger.exception(f"{e}")
        return HTTPException(status_code=500, detail=f"{e}")
