from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.subscription_status import SubscriptionStatus, SubscriptionStatusCreate, SubscriptionStatusBase


class CRUDSubscriptionStatus(CRUDBase[SubscriptionStatus, SubscriptionStatusCreate, SubscriptionStatusBase]):
    pass


subscription_status = CRUDSubscriptionStatus(SubscriptionStatus)
