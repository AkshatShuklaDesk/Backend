from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.module import Module, ModuleCreate, ModuleBase


class CRUDModule(CRUDBase[Module, ModuleCreate, ModuleBase]):
    pass


module = CRUDModule(Module)
