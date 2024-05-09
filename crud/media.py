from typing import List, Dict
import time
from fastapi import UploadFile
from datetime import datetime
from fastapi.encoders import jsonable_encoder
import base64
from io import BytesIO
from PIL import Image
from sqlalchemy import desc
from sqlalchemy.orm import Session
from crud.base import CRUDBase
import os
from models.media import Media
from schemas.media import MediaBase , MediaCreate
import crud

def decode_base64_to_image(base64_string, output_filename,output_directory):
    try:
        # Remove potential newlines and extra spaces
        base64_string = base64_string.replace('\n', '').replace('\r', '').strip()

        # Add padding if necessary to make the string length a multiple of 4
        padding = '=' * (-len(base64_string) % 4)
        base64_string += padding

        # Attempt to decode the base64 string
        image_data = base64.b64decode(base64_string, validate=True)

        # Create an image from the decoded data and save it
        image_path = os.path.join(output_directory, output_filename)
        image = Image.open(BytesIO(image_data))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image.save(image_path)
        print(f"Image saved as '{output_filename}'")
    except (base64.binascii.Error, ValueError) as e:
        print(f"Error decoding base64 string: {e}")
        # Handle the error accordingly (e.g., log the error, exit the function, etc.)
    except IOError as e:
        print(f"Error in saving the image: {e}")

class CRUDImage(CRUDBase[Media, MediaCreate, MediaBase]):

    def upload_pod_image(self, directory_name: str, pod_image: UploadFile,client_name:str,type : str , image_id : str):
        print(directory_name)
        '''Check valid extension'''
        ext = (".png", ".jpg", ".jpeg", ".gif")
        valid_ext = pod_image.filename.endswith(ext)
        if valid_ext:
            extension = os.path.splitext(pod_image.filename)[1]
            image_name = f"{client_name}_{image_id}_{type}{extension}"
            if not os.path.exists(directory_name):
                os.makedirs(directory_name)
            file_path = os.path.join(directory_name, image_name)
            with open(file_path, "wb+") as image_file_upload:
                data = pod_image.file.read()
            data = str(data)
            data = data.split(",")[1][:-1]
            decode_base64_to_image(data, image_name,directory_name)

            return f"{image_name}"
        return None

    def save_pod_image(self, db: Session, pod_image: str, bilty_id: int):
        pod_image_in = {
            "bilty_id": bilty_id,
            "pod_image": pod_image
        }
        db_obj = self.model(**pod_image_in)  # type: ignore
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)

        return db_obj

    def save_image(self,db :Session , image_id:str,image:str,type:str ):
        image_in = {
            "image_id" : image_id,
            "type" : type,
            "image" : image,
            "created_date" : datetime.now()
        }
        db_obj=crud.Media_Image.create(db=db,obj_in=image_in)
        # vehicle = db.query(s)
        
        return db_obj
    
    def get_media_by_image_id(self, db:Session , image_id :str , type : str):
        return db.query(self.model).filter(self.model.image_id == image_id , self.model.type == type).order_by(self.model.created_date.desc()).first()


Media_Image = CRUDImage(Media)
