import json
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from scripts import utilities

router = APIRouter()


@router.get("/{pincode}")
def fetch_area_details(
    *,
    pincode: Optional[str] = None
) -> Any:
    response = utilities.fetch_area_details_from_pincode(pincode)
    return response
