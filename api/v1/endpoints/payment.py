from fastapi.responses import FileResponse
import razorpay
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Request, Form, Depends
from integrations.razorpay import create_payment_order, verify_payment
from starlette.templating import Jinja2Templates
from sqlmodel import Session
from crud import account_transaction
import datetime
from api.deps import get_db
import crud
import logging
from core.logging_utils import setup_logger
templates = Jinja2Templates(directory="templates")
import os
RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
RAZORPAY_API_SECRET = os.getenv('RAZORPAY_API_SECRET')

log_name = "payment"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()

@router.post("/razorpay")
async def razorpay_payment(
        request: Request,
        amount: int = Form(...),
        db: Session = Depends(get_db),
        company_id:int = Form(...),
):
    try:
        payment_order_info = create_payment_order(amount=amount)
        obj_in = {'payment_order_id':payment_order_info['id'],'amount':amount/100,'status':'pending','user_id':company_id}
        obj_in['created_date'] = obj_in['modified_date'] = datetime.datetime.now()
        obj = crud.payment_status_details.create(db=db,obj_in=obj_in)
        db.commit()
        return payment_order_info
    except Exception as e:
        logger.error(f'Exception in payment order : {e}')
        return {"error": str(e)}
    
    
@router.post('/verify-payment')
async def verify_payment(db:Session = Depends(get_db),
                         razorpay_signature: str = Form(...),
                         razorpay_order_id: str = Form(...),
                         razorpay_payment_id: str = Form(...)
                         ):
    try:
        payment_status = verify_payment(razorpay_signature=razorpay_signature,razorpay_order_id=razorpay_order_id,
                       razorpay_payment_id=razorpay_payment_id)
        payment_order_info = crud.payment_status_details.get_by_payment_order_id(db=db,order_id=razorpay_order_id)
        user_obj = crud.company.get(db=db,id=payment_order_info.user_id)
        new_wallet_balance = user_obj.wallet_balance or 0 + payment_order_info.amount
        if user_obj.wallet_balance:
            new_wallet_balance = user_obj.wallet_balance + payment_order_info.amount
        else:
            new_wallet_balance = payment_order_info.amount
        crud.company.update(db=db,db_obj=user_obj,obj_in={'wallet_balance':new_wallet_balance})
        # payment_order_info.pop('id')
        crud.payment_status_details.update(db=db, db_obj=payment_order_info, obj_in={'status':'Done','modified_date':datetime.datetime.now()})
        crud.account_transaction.recharge_transaction(db=db, order_obj=payment_order_info)
        db.commit()
        return {'status':'Payment Verified'}
    except Exception as e:
        logger.error(f'Exception in payment verification : {e}')
        return {"error": str(e)}
