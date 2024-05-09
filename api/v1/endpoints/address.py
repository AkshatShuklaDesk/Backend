from typing import Any, List,Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from fastapi.encoders import jsonable_encoder

import crud, models,schemas
from api.deps import get_db
from integrations.delhivery import DelhiveryClient
from schemas.delhivery.warehouse import CreateWarehouse

# this is temporary till user auth flow gets implemented
from temp import test_user
from core.logging_utils import setup_logger
import logging

log_name = "address"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()


@router.post("/")
def save_address(
        *,
        db: Session = Depends(get_db),
        address_in: schemas.AddressInfo,
        created_by:int
) -> Any:
    """
    Save new address
    """
    try:
        address_in_json = jsonable_encoder(address_in)
        logger.info(f'Save pickup address args : {address_in_json}')
        address_in_json['created_by'] = created_by
        address = crud.address.check_save_user_address(db=db, address_in=address_in_json)
        address = jsonable_encoder(address)
        address['email_address'] = address_in.email_address
        address['contact_no'] = address_in.contact_no
        result = {'address': jsonable_encoder(address)}
        crud.partner.create_warehouse(address=address)
        db.commit()
        return result
    except Exception as e:
        logger.error(f'Error in save address api :- {e}')
        return


@router.get("/")
def get_user_address(
    *,
    db: Session = Depends(get_db),
    user_id:int
) -> Any:
    """
    Save new address
    """
    try:
        addresses = crud.address.get_address_by_user(db=db, user_id=user_id)
        return addresses
    except Exception as e:
        print(f'Error in get address api :- {e}')
        return


# @router.put("/{id}")
# def update_product(
#     *, db: Session = Depends(get_db), id: int, product_in: models.ProductUpdate
# ) -> Any:
#     """
#     Update User.
#     """
#     product = crud.product.get(db=db, id=id)
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     product = crud.product.update(db=db, db_obj=product, obj_in=product_in)
#     return product
#
#
# #
# #
# @router.get("/{id}")
# def get_product(*, db: Session = Depends(get_db), id: int) -> Any:
#     """
#     Get item by ID.
#     """
#     product = {}
#     product = crud.product.get(db=db, id=id)
#     if not product:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return product
#
#
# @router.delete("/{id}")
# def delete_product(
#     *,
#     db: Session = Depends(get_db),
#     id: int,
# ) -> Any:
#     """
#     Delete an item.
#     """
#     product = crud.product.get(db=db, id=id)
#     if not product:
#         raise HTTPException(status_code=404, detail="Item not found")
#     product = crud.product.remove(db=db, id=id)
#     return product
#
# @router.post("/filter")
# def filter_product(
#     *,
#     db: Session = Depends(get_db),
#     filter_in: Dict = None,
# ) -> Any:
#     """
#     This is normal searching API
#     Filter_fields : {"column_name":"value","search":"like" or "starts_with" or "eq"}
#     Direct table column value search with only single filter
#     """
#     filter_condition = crud.modify_filter(filter_in)
#     product = crud.product.dynamic_filter(db=db,filter_condition=filter_condition)
#     if not product:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return product
