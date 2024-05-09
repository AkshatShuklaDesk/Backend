from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.package_type import PackageType, PackageTypeCreate, PackageTypeBase


class CRUDPackageType(CRUDBase[PackageType, PackageTypeCreate, PackageTypeBase]):
    pass


package_type = CRUDPackageType(PackageType)
