from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.plan_type import PlanType, PlanTypeCreate, PlanTypeBase


class CRUDPlanType(CRUDBase[PlanType, PlanTypeCreate, PlanTypeBase]):
    pass


plan_type = CRUDPlanType(PlanType)
