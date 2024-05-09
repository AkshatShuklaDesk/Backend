import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import crud
from crud.base import CRUDBase
from models.indent import Indent, IndentBase, IndentCreate
from fastapi import HTTPException


class CRUDIndent(CRUDBase[Indent, IndentCreate,IndentBase]):
   def create_indent(self,db,indent):
      indent["created_date"] = datetime.datetime.now()
      db_obj = crud.Indent.create(db=db,obj_in=indent)
      
      return db_obj

   def get_indents(self,db:Session,created_by):
      indent_obj = db.query(self.model).filter(self.model.created_by == created_by).order_by(self.model.id.desc()).all()
      indent_obj = jsonable_encoder(indent_obj)
      return indent_obj

   def create_mutliple(self,db:Session,indents:List):
      db_obj = crud.Indent.create_multi(db=db,obj_in=indents)
      return db_obj

   def update_indent(self,db:Session,indent_info,indent_in):
      indent_in["modified_date"] = datetime.datetime.now()
      update_obj = crud.Indent.update(db=db,db_obj=indent_info,obj_in=indent_in)
      return update_obj
   
   def set_confirmation(self,db:Session,status):
      updated_indent=crud.Indent.get(db=db,id=status["id"])
      user_id=updated_indent.created_by
      user_info=crud.users.get(db=db,id=user_id)

      if status["status_code"]==3:
         updated_indent.trip_status = 3
      else:
         if not user_info.wallet_balance<updated_indent.actual_price:
            updated_indent.trip_status = 2
         else:
            raise HTTPException(status_code=401, detail=f"error : insufficient balance")

      old_indent=crud.Indent.get(db=db,id=status["id"])
      update_obj = crud.Indent.update(db=db,db_obj=old_indent,obj_in=updated_indent)

      return update_obj
   
   def set_admin_price(self,db:Session,price):
      updated_indent=crud.Indent.get(db=db,id=price["id"])
      updated_indent.actual_price=price["price"]
      updated_indent.trip_status=1
      old_indent=crud.Indent.get(db=db,id=price["id"])
      update_obj = crud.Indent.update(db=db,db_obj=old_indent,obj_in=updated_indent)

      return update_obj
Indent = CRUDIndent(Indent)