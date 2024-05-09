from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.address_type import AddressType, AddressTypeCreate, AddressTypeBase


class CRUDAddressType(CRUDBase[AddressType, AddressTypeCreate, AddressTypeBase]):
    pass


address_type = CRUDAddressType(AddressType)