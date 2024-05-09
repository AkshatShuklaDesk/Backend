from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.users_role import UsersRole, UsersRoleCreate, UsersRoleBase


class CRUDUsersRole(CRUDBase[UsersRole, UsersRoleCreate, UsersRoleBase]):
    pass


users_role = CRUDUsersRole(UsersRole)
