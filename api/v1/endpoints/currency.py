from typing import Any, List,Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

import crud, models
from api.deps import get_db
from fastapi.encoders import jsonable_encoder

# this is temporary till user auth flow gets implemented
from temp import test_user

router = APIRouter()


@router.get("/")
def get_currency(*, db: Session = Depends(get_db)) -> Any:
    """
    Get item by ID.
    """

    currency = crud.currency.get_multi(db=db)
    currency = jsonable_encoder(currency)
    if not currency:
        raise HTTPException(status_code=404, detail="Item not found")
    return currency
