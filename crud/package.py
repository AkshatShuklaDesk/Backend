from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.package_type import PackageType
from models.package import Package, PackageCreate, PackageBase


class CRUDPackage(CRUDBase[Package, PackageCreate, PackageBase]):
    def get_package_details(self,db:Session,id):
        package = db.query(self.model,PackageType.name).outerjoin(PackageType,PackageType.id == self.model.type_id)\
            .filter(self.model.id == id).first()
        if not package:
            return {}
        package_detail = {**jsonable_encoder(package[0]),"type_name":package[1]}
        return package_detail
    pass


package = CRUDPackage(Package)
