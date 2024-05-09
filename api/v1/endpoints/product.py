import os
from typing import Any, List,Dict
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session
import pandas as pd
import constants
import crud, models
from api.deps import get_db
from auto_mailing import send_mail

# this is temporary till user auth flow gets implemented
from temp import test_user
from core.logging_utils import setup_logger
import logging
log_name = "product"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()

_file_name = 'product.py'

@router.post("/")
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: models.ProductCreate,
) -> Any:
    """
    This will create a new product
    """
    product = crud.product.create(db=db, obj_in=product_in)
    result = {'product_id': product.id}
    db.commit()
    return result

@router.put("/{id}")
def update_product(
    *, db: Session = Depends(get_db), id: int, product_in: models.ProductUpdate
) -> Any:
    """
    Update User.
    """
    product_in = product_in.model_dump(exclude_unset=True)
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = crud.product.update(db=db, db_obj=product, obj_in=product_in)
    result = {'product_id': product.id}
    db.commit()
    return result


@router.get("/{id}")
def get_product(*, db: Session = Depends(get_db), id: int) -> Any:
    """
    Get item by ID.
    """

    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Item not found")
    return product


@router.delete("/{id}")
def delete_product(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> Any:
    """
    Delete an item.
    """
    product = crud.product.get(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Item not found")
    product = crud.product.remove(db=db, id=id)
    db.commit()
    return product

@router.post("/filter")
def filter_product(
    *,
    db: Session = Depends(get_db),
    filter_in: Dict = None,
) -> Any:
    """
    This is normal searching API
    Filter_fields : {"column_name":"value","search":"like" or "starts_with" or "eq"}
    Direct table column value search with only single filter
    """
    filter_condition = crud.modify_filter(filter_in)
    product = crud.product.dynamic_filter(db=db,filter_condition=filter_condition)
    if not product:
        raise HTTPException(status_code=404, detail="Item not found")
    return product

@router.get("/get_product_details/")
def get_product_details(
        *,
        db:Session = Depends(get_db)
):
    product_details = crud.product.get_product_details(db=db)
    return product_details

@router.get("/send_product_mail/")
def get_product_details(
        *,
        db:Session = Depends(get_db)
):
    product_details = crud.product.get_product_details(db=db)
    details_to_send = []
    for details in product_details:
        temp_dict = {}
        temp_dict['name'] = details['name']
        temp_dict['sku'] = details['sku']
        temp_dict['length'] = details['length']
        temp_dict['width'] = details['width']
        temp_dict['height'] = details['height']
        temp_dict['volumetric weight'] = details['volumetric_weight']
        temp_dict['unit price']  = details['unit_price']
        temp_dict['category'] = details['category']
        details_to_send.append(temp_dict)

    for mail in constants.mail_list:
        send_mail(data=details_to_send, receiver_mail=mail, cc="", mode="Product Report", file="product_details")

    return product_details


@router.post("/add_product_catalogue")
async def upload_catalogue(
        *,
        db: Session = Depends(get_db),
        excel_file: UploadFile = File(...)
) -> Any:
    try:
        os.makedirs(constants.UPLOAD_EXCEL_DIR, exist_ok=True)
        file_path = os.path.join(constants.UPLOAD_EXCEL_DIR, excel_file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await excel_file.read())
 
        df = pd.read_excel(file_path,dtype='object')
        df.columns = df.columns.str.lower()

        for index,row in df.iterrows():
            product = row.to_dict()
            crud.product.create(db=db,obj_in=product)
        db.commit()
    except Exception as e:
        logger.error(f"Error in catalogue save API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")
    
@router.get("/get_sample_file/")
def get_sample_file(
    *,
    db : Session = Depends(get_db)
):
    try:
        file_path = "product.xlsx"
        return FileResponse(file_path)
    except Exception as e:
        logger.error(f"Error in getting sample API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")
    
    