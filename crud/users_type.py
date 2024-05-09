from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.users_type import UsersType, UsersTypeCreate, UsersTypeBase


class CRUDUsersType(CRUDBase[UsersType, UsersTypeCreate, UsersTypeBase]):
    pass


users_type = CRUDUsersType(UsersType)
