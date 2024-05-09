import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import crud
from crud.base import CRUDBase
from models import Users
from models.address import Address, AddressCreate, AddressBase


class CRUDAddress(CRUDBase[Address, AddressCreate, AddressBase]):
    def check_save_user_address(self,db:Session,address_in):
        user_in = {'contact_no':address_in.pop('contact_no'),'first_name':address_in.pop('first_name'),'email_address':address_in.pop('email_address')}
        user = crud.users.check_and_create_user(db=db,user_in=user_in)
        address_in['users_id'] = user.id
        address_in['created_date'] = address_in['modified_date'] = datetime.datetime.now()
        if not address_in.get("complete_address"):
            if "line2" in address_in and address_in["line2"] is not None:
                address_in["complete_address"]=address_in["line1"]+address_in["line2"]
            else:
                address_in["complete_address"]=address_in["line1"] if "line1" in address_in else None
        address = self.create(db=db,obj_in=address_in)
        return address

    def update_address_info(self,db:Session,add_in):
        add_obj = self.get(db=db,id=add_in['id'])
        address = self.update(db=db,db_obj=add_obj,obj_in=add_in)
        return address

    def get_address_by_user(self, db: Session, user_id):
        addresses = db.query(self.model).filter(self.model.created_by == user_id).all()

        user = db.query(Users).filter(Users.id == user_id).first()

        if not user:
            return None

        user_details = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "contact_no": user.contact_no,
            "email_address": user.email_address
        }

        results = []
        for address in addresses:
            address_dict = {**jsonable_encoder(address), **user_details}
            results.append(address_dict)

        return results



address = CRUDAddress(Address)
