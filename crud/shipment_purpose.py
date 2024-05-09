from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.shipment_purpose import ShipmentPurpose, ShipmentPurposeCreate, ShipmentPurposeBase


class CRUDShipmentPurpose(CRUDBase[ShipmentPurpose, ShipmentPurposeCreate, ShipmentPurposeBase]):
    pass


shipment_purpose = CRUDShipmentPurpose(ShipmentPurpose)
