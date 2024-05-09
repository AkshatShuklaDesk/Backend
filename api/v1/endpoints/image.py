import os
from typing import Any, List,Dict

from fastapi import APIRouter, Depends, HTTPException,UploadFile, File, Response

import crud

# this is temporary till user auth flow gets implemented
from temp import test_user
from core.logging_utils import setup_logger
import logging
log_name = "image"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()


@router.post("/upload_image")
def upload_image(
        product_id: int,
        file: UploadFile = File(...)
):
    try:
        directory_name = 'static_image_dir'
        image = crud.product.upload_image(directory_name=directory_name, image=file, product_id=product_id)
        return {"filepath": image}
    except Exception as e:
        print(f'Exception in upload image : {e}')


@router.get("/get_image")
def fetch_image(
        file_path: str
):
    directory_name = 'static_image_dir'
    image = crud.product.get_image(file_path=file_path)
    return Response(content=image, media_type="image/png")

@router.delete("/delete_image")
def delete_image(
        file_path: str
):
    try:
        os.remove(file_path)
        return {"success": True}
    except Exception as e:
        print(f'Exception in delete image api : {e}')
        return {"success": False}