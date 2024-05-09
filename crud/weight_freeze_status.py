import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.weight_freeze_status import WeightFreezeStatus, WeightFreezeStatusCreate, WeightFreezeStatusBase


class CRUDWeightFreezeStatus(CRUDBase[WeightFreezeStatus, WeightFreezeStatusCreate, WeightFreezeStatusBase]):
    def get_by_name(self,db:Session,name):
        status = db.query(self.model).filter(self.model.name==name).first()
        return status
    pass


weight_freeze_status = CRUDWeightFreezeStatus(WeightFreezeStatus)
