import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import constants
import os
from crud.base import CRUDBase
from models.product import Product, ProductCreate, ProductBase
from models.order_product import OrderProduct , OrderProductBase , OrderProductCreate
from models.order import Order
import base64
from scripts.utilities import random_with_N_digits, decode_base64_to_image


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductBase]):

    def generate_sku_code(self,db:Session):
        skus = db.query(self.model.sku).all()
        skus = list(x[0] for x in skus)
        random_sku = None
        for i in range(constants.SKU_CREATION_RETRY):
            random_sku = random_with_N_digits(13)
            if str(random_sku) not in skus:
                break
        return random_sku

    def check_and_save_products(self,db:Session,product_in,user_id):
        products = []
        for product in product_in:
            if 'id' in product and product['id']:
                products.append({'id':product['id'],'unit_price':product.pop('unit_price'),'quantity':product.pop('quantity')})
                continue
            product['sku'] = self.generate_sku_code(db=db) if not product['sku'] else product['sku']
            product['created_by'] = product['modified_by'] = user_id
            product['created_date'] = product['modified_date'] = datetime.datetime.now()
            prod = self.create(db=db,obj_in=product)
            products.append({'id': prod.id, 'unit_price': product.pop('unit_price'), 'quantity': product.pop('quantity')})
        return products

    def update_product_info(self,db:Session,product_info_list,user_id):
        updated_obj_list = []
        for product in product_info_list:
            prod_object = self.get(db=db,id=product.pop('id'))
            product['modified_by'] = user_id
            product['modified_date'] = datetime.datetime.now()
            updated_obj = self.update(db=db,db_obj=prod_object,obj_in=product)
            updated_obj_list.append(updated_obj)
        return updated_obj_list

    def upload_image(self,directory_name, image, product_id, tag=""):
        print(directory_name)
        '''Check valid extension'''
        ext = (".png", ".jpg", ".jpeg", ".gif")
        valid_ext = image.filename.endswith(ext)
        if valid_ext:
            filename,extension = os.path.splitext(image.filename)
            image_name = f"{product_id}-{tag}-{filename}{extension}"
            if not os.path.exists(directory_name):
                os.makedirs(directory_name)
            file_path = os.path.join(directory_name, image_name)
            data = image.file.read()
            data = base64.b64encode(data).decode('utf-8')
            data = str(data)
            # data = data.split(",")[1][:-1]
            decode_base64_to_image(data, image_name, directory_name)

            return f"{file_path}"

    def get_image(self, file_path):
        with open(file_path,'rb') as image:
            data = image.read()
        return data

    def get_from_sku(self,db, sku):
        product = db.query(self.model).filter(self.model.sku == sku).first()
        return product

    def get_product_details(self,db:Session):
        product_details = db.query(self.model).all()
        product_details = jsonable_encoder(product_details)
        return product_details



product = CRUDProduct(Product)
