from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.product_package import ProductPackage, ProductPackageCreate, ProductPackageBase


class CRUDProductPackage(CRUDBase[ProductPackage, ProductPackageCreate, ProductPackageBase]):
    pass


product_package = CRUDProductPackage(ProductPackage)
