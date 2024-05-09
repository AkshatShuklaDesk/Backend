import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.weight_discrepancy_status import WeightDiscrepancyStatus, WeightDiscrepancyStatusCreate, WeightDiscrepancyStatusBase


class CRUDWeightDiscrepancyStatus(CRUDBase[WeightDiscrepancyStatus, WeightDiscrepancyStatusCreate, WeightDiscrepancyStatusBase]):
    def get_by_name(self,db:Session,name):
        status = db.query(self.model).filter(self.model.name == name).first()
        return status


weight_discrepancy_status = CRUDWeightDiscrepancyStatus(WeightDiscrepancyStatus)
