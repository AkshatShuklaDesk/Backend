import crud
from db.session import SessionLocal


# ses = Depends(get_db())
#
def add_order_status(db= SessionLocal()):

    st1 = crud.order_status.create(db=db,obj_in={"name":'new'})
    st2 = crud.order_status.create(db=db, obj_in={"name": 'invoiced',"parent_id": st1.id})
    db.commit()


def add_order_type(db=SessionLocal()):
    st1 = crud.order_type.create(db=db, obj_in={"name": 'domestic'})
    st2 = crud.order_type.create(db=db, obj_in={"name": 'international'})
    db.commit()

def add_payment_type(db=SessionLocal()):
    st1 = crud.payment_type.create(db=db, obj_in={"name": 'cod'})
    st2 = crud.payment_type.create(db=db, obj_in={"name": 'prepaid'})
    db.commit()

def add_test_user(db=SessionLocal()):
    st1 = crud.users.create(db=db, obj_in={"first_name": 'yash',"last_name": 'shah'})
    db.commit()


# add_order_status()
# add_order_type()
# add_payment_type()
# add_test_user()