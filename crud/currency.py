from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.currency import Currency, CurrencyCreate, CurrencyBase


class CRUDCurrency(CRUDBase[Currency, CurrencyCreate, CurrencyBase]):
    pass


currency = CRUDCurrency(Currency)
