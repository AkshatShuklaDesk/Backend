import datetime
from typing import Any, List,Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
import crud, models, schemas
from api import deps
from core.logging_utils import setup_logger
import logging
from crud import account_transaction
from schemas import account_transaction
log_name = "account_transaction"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()
@router.post("/", response_model=Dict)
def save_account_transaction(
    *,
    db: Session = Depends(deps.get_db),
    account_transaction_in:schemas.AccountTransactionCreate
) -> Any:
    try:
        created_date = account_transaction_in.account_transaction_info[0].created_date
        account_transaction_in = jsonable_encoder(account_transaction_in)
        account_transaction_info = account_transaction_in.pop('account_transaction_info')
        if account_transaction_info:
            fyear_save = account_transaction_info[0]['fyear']
            date_to_save = str(account_transaction_info[0]['date']).split('T')[0]
            date_to_save = datetime.datetime.strptime(date_to_save, "%Y-%m-%d")
            fyear_start, fyear_end = str(fyear_save).split("-")
            fyear_start = "20" + fyear_start
            fyear_end = "20" + fyear_end

            fyear_start_date = datetime.datetime(int(fyear_start), 4, 1)
            fyear_end_date = datetime.datetime(int(fyear_end), 3, 31)
            if fyear_start_date > date_to_save or fyear_end_date < date_to_save:
                raise HTTPException(status_code=506, detail='Date is not as Per Financial Year.')
        logger.info(f'Voucher Save Argument :- {account_transaction_info}')
        account_transaction = crud.account_transaction.account_transaction.create_account_transaction_entry(db=db, account_obj=account_transaction_info[0])
        output_dict = {"id": account_transaction}
        db.commit()
        return output_dict

    except Exception as e:
        logger.exception(f'Exception in create pod statement API :- {e}')
        return HTTPException(status_code=401, detail="Exception in API")

@router.post("/account_report",response_model=Dict)
def get_account_report(
    *,
    db: Session = Depends(deps.get_db),
    filter_dict:Dict,
    page_number: int = 1,
    page_size: int = 10
):
    try:
        offset = (page_number - 1) * page_size
        account_transaction_list = crud.account_transaction.get_account_transaction_report(db=db,filter_dict=filter_dict,offset=offset,limit=page_size)
        account_transaction_list = jsonable_encoder(account_transaction_list)
        output_dict = {"report": account_transaction_list}
        return output_dict
    except Exception as e:
        logger.exception(f'Exception in create pod statement API :- {e}')
        return HTTPException(status_code=401, detail="Exception in API")
