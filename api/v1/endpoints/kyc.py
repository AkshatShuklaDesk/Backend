from typing import Any,Dict
from fastapi import APIRouter, Depends, HTTPException,UploadFile,File
import requests
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
import constants
import crud
from crud import *
import os
from api import deps
from core.logging_utils import setup_logger
import logging
import numpy as np
import schemas
# from utilities import custom_exception

log_name = "pod_image"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()

# @router.post("/",response_model=Dict,description="save pod image")
# def save_pod_image(
#     *,
#     db: Session = Depends(deps.get_db),
#     pod_image : UploadFile = File(...),
#     image_id : str,
#     client_name : str,
#     type : str
# ) -> Any:
#     try:
#         logger.info(f'------------- POD image API called ----------')
#         logger.info(f'POD image Argument :- {image_id}')
#         directory_name = constants.UPLOADED_IMG_PATH
#         pod_image = crud.Media_Image.upload_pod_image(directory_name=directory_name,pod_image=pod_image,client_name= client_name, type=type , image_id = image_id)
#         if pod_image and image_id:
#             pod_img_dict = crud.Media_Image.save_image(db=db,image=pod_image,image_id=image_id,type = type)
#         pod_img_dict = jsonable_encoder(pod_img_dict)
#         db.commit()
#         logger.info(f'------------- POD image saved ----------')
#         return pod_img_dict
#     except Exception as e:
#         logger.exception(f'Exception in save pod image API :- {e}')
#         return HTTPException(status_code=401, detail="Exception in API")

# @router.get("/",description="get bilty using excel")
# def get_pod_image(
#     *,
#     db: Session = Depends(deps.get_db),
#     bilty_id: str
# ) -> Any:
#     try:
#         logger.info(f'------------- Get POD image API called ----------')
#         logger.info(f'POD image Argument :- {bilty_id}')
#         kyc_img_name = crud.Media_Image.get_media_by_image_id(db=db,image_id=bilty_id , type = "bilty_pod")
#         if not kyc_img_name:
#             raise custom_exception.PodImageNotFound
#         kyc_img_name = jsonable_encoder(kyc_img_name)
#         kyc_img_name = kyc_img_name['image']
#         logger.info(f'POD image name :- {kyc_img_name}')

#         directory_name = constants.UPLOADED_IMG_PATH
#         img_path = f'{directory_name}/{kyc_img_name}'
#         logger.info("pod image path="+str(img_path))
#         return FileResponse(img_path)

#     except custom_exception.PodImageNotFound as e:
#         logger.info(f'Pod image Not Found.')
#         raise HTTPException(status_code=406, detail="Pod image Not Found.")
#     except Exception as e:
#         logger.exception(f'Exception in get pod image API :- {e}')
#         return HTTPException(status_code=401, detail="Exception in API")

@router.post("/upload_selfie")
async def save_selfie(
        *,
        image_id : str,
        user_name : str,
        file: UploadFile = File(...),
        db : Session = Depends(deps.get_db),
        type : str,

) -> Any:
    try:
        logger.info(f'------------- Fetching image ----------')
        file_content = await file.read()
        await file.seek(0)

        extension = os.path.splitext(file.filename)[1]
        filename = f"{user_name}_{image_id}_{type}{extension}"
        if not os.path.exists(constants.UPLOADED_IMG_PATH):
            os.makedirs(constants.UPLOADED_IMG_PATH)
        save_path = os.path.join(constants.UPLOADED_IMG_PATH, filename)
        with open(save_path, "wb") as image_file:
            image_file.write(file_content)
        logger.info(f'------------- In save image CRUD ----------')
        declaration_image_dict = crud.Media_Image.save_image(db=db, image_id=image_id, type=type, image=filename)

        logger.info(f'------------- Out of save image CRUD ----------')
        db.commit()
        logger.info(f'------------- POD image saved ----------')
        if declaration_image_dict:

            return {"status":"success"}
    except Exception as e:
        logger.exception(f"{e}")
        raise HTTPException(status_code=406, detail=f"{e}")
    

@router.post("/generate_otp")
def generate_otp(id_number):
    if not id_number:
        return {'error': 'ID number is required'}
    
    api_url = 'https://kyc-api.surepass.io/api/v1/aadhaar-v2/generate-otp'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {constants.surepass_token}'}
    data = {'id_number': id_number}

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        return {'message': 'OTP generated successfully'}
    else:
        return {'error': 'Failed to generate OTP', 'details': response.text}

@router.post("/submit_otp")
def submit_otp(client_id: str, otp: str):
    if not client_id or not otp:
        raise HTTPException(status_code=400, detail='Client ID and OTP are required')

    api_url = 'https://kyc-api.surepass.io/api/v1/aadhaar-v2/submit-otp'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {constants.surepass_token}'}
    data = {'client_id': client_id, 'otp': otp}

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        return {'message': 'OTP submitted successfully'}
    else:
        raise HTTPException(status_code=500, detail='Failed to submit OTP', response=response.text)
    

@router.get("/",description="Get kyc image")
def get_pod_image(
    *,
    db: Session = Depends(deps.get_db),
    id: str,
    type:str,
) -> Any:
    try:
        logger.info(f'------------- Get kyc image API called ----------')
        logger.info(f'kyc image Argument :- {id}')
        kyc_img_name = crud.Media_Image.get_media_by_image_id(db=db,image_id=id , type = type)
        if not kyc_img_name:
            return HTTPException(status_code=401,detail="image not found")
        kyc_img_name = jsonable_encoder(kyc_img_name)
        kyc_img_name = kyc_img_name['image']
        logger.info(f'kyc image name :- {kyc_img_name}')

        directory_name = constants.UPLOADED_IMG_PATH
        img_path = f'{directory_name}/{kyc_img_name}'
        logger.info("kyc image path="+str(img_path))
        return FileResponse(img_path)

    except Exception as e:
        logger.exception(f'Exception in get kyc image API :- {e}')
        return HTTPException(status_code=401, detail="Exception in API")
    

@router.post("/kyc_status/")
def kyc_status(client_type: str, status: int, id:int, db: Session = Depends(deps.get_db)):
    try:
        if client_type == "company":
            company=crud.company.get(db=db,id=id)
            company.kyc_status_id=status
            db.commit()
        if client_type=="user":
            user=crud.users.get(db=db,id=id)
            user.kyc_status_id=status
            db.commit()
        return {"status":True,"message":"KYC done"}
    except Exception as e:
        return HTTPException(status_code=401,detail={"Exception in api":{e} })


    
