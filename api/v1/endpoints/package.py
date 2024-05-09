from typing import Any, List,Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

import crud, models
import datetime
from api.deps import get_db

# this is temporary till user auth flow gets implemented
from temp import test_user
_file_name = 'package.py'
router = APIRouter()


@router.post("/")
def create_package(
    *,
    db: Session = Depends(get_db),
    package_in: models.PackageCreate
) -> Any:
    """
    This will create a new package
    """
    try:
        package_info = jsonable_encoder(package_in)
        package_info['created_date'] = package_info['modified_date'] = datetime.datetime.now()
        package = crud.package.create(db=db, obj_in=package_info)
        result = {'package_id': package.id}
        db.commit()
        return result
    except Exception as e:
        print(f'Error in create_package API from {_file_name} :- {e}')


@router.put("/{id}")
def update_package(
    *,
    db: Session = Depends(get_db),
    id: int,
    package_in: models.PackageCreate
) -> Any:
    """
    Update User.
    """
    package_in = package_in.model_dump(exclude_unset=True)
    package_info = crud.package.get(db=db, id=id)
    if not package_info:
        raise HTTPException(status_code=404, detail="package not found")

    try:
        package_in = jsonable_encoder(package_in)
        package_in['modified_date'] = datetime.datetime.now()
        updated_package = crud.package.update(db=db, db_obj=package_info, obj_in=package_in)
        result = {'package_id': updated_package.id}
        db.commit()
        return result
    except Exception as e:
        print(f'Error in update package API from {_file_name} :- {e}')

@router.get("/{id}")
def get_package(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    """
    Get package by ID.
    """
    method_name = 'get_package'
    try:
        package_info = crud.package.get_package_details(db=db, id=id)
        return package_info
    except Exception as e:
        print(f'Error in {method_name} API from {_file_name} :- {e}')

@router.delete("/{id}")
def delete_package(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> Any:
    """
    Delete an item.
    """
    method_name = 'delete_package'

    package_info = crud.package.get(db=db, id=id)
    if not package_info:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        package_info = crud.package.remove(db=db, id=id)

        db.commit()
        # print('package_info : ', type(package_info))
        return package_info
    except Exception as e:
        print(f'Error in {method_name} API from {_file_name} :- {e}')