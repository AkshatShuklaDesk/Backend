from collections import defaultdict
from datetime import date, time, timedelta, datetime
from typing import Annotated, Any, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlmodel import Session
import crud
import constants
from crud import account_transaction
from db.session import SessionLocal
from integrations.dtdc import DTDCClient
import schemas
from integrations.delhivery import DelhiveryClient
from api.deps import get_db
from models import OrderStatus
from schemas.common import TrackingResponse,PartnerInfo,CancelShipmentInfo
from schemas.delhivery.shipment import (
    PickupDateTime,
    PickupDetail,
)
from core.logging_utils import setup_logger
import logging
from scripts.order import create_order_info_from_file
from integrations.xpress import xpressClient
from integrations.ecomexpress import ecomExpress
from integrations.maruti import maruti

# this is temporary till user auth flow gets implemented
from temp import test_user
from auto_mailing import send_mail
from schemas.xpressbees import waybill

log_name = "order"
endpoint_device_logger_setup = setup_logger(log_name, level="INFO")
logger = logging.getLogger(log_name)

router = APIRouter()


@router.post("/")
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: schemas.OrderCreate,
    user_id:int
) -> Any:
    """
    Create new order.
    """
    try:
        logger.info(f"create order args : {jsonable_encoder(order_in)}")
        order = crud.order.create_order(
            db=db, order_in=order_in, user=user_id, logger=logger
        )
        result = jsonable_encoder(order)
        get_pickup_address = crud.address.get(db=db,id=result['pickup_address_id'])

        get_drop_address = crud.address.get(db=db, id=result['drop_address_id'])
        buyer_name = crud.users.get(db=db,id=result['buyer_id'])
        user_name = crud.users.get(db=db,id=result['users_id'])
        get_pickup_address = jsonable_encoder(get_pickup_address)
        get_drop_address = jsonable_encoder(get_drop_address)
        buyer_name = jsonable_encoder(buyer_name)
        user_name = jsonable_encoder(user_name)

        result['pickup address'] = get_pickup_address['complete_address']
        result['drop address'] = get_drop_address['complete_address']
        result['buyer name'] = buyer_name['first_name']
        result['user name'] = user_name['first_name']
       
        keys_without_id = [key.replace('_id', '').replace('_', ' ') if '_id' in key else key for key in result.keys()]
        final_dict = dict(zip(keys_without_id, list(result.values())))
        #for mail in constants.mail_list:
        #    send_mail(data=[final_dict], receiver_mail=mail, cc="",mode="Order Creation",file="ordercreation")
        db.commit()
        return result
    except Exception as e:
        logger.error(f"Error in order save API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.put("/")
def update_order(
    *, db: Session = Depends(get_db), order_in: schemas.OrderUpdate, id: int
) -> Any:
    """
    Create new user.
    """
    try:
        logger.info(f" update order args for id {id} :- {jsonable_encoder(order_in)}")
        updated_order = crud.order.update_order(
            db=db, order_in=order_in, id=id, user=test_user
        )
        result = {"data": updated_order}
        db.commit()
        return result
    except Exception as e:
        logger.info(f"Error in order update API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")



@router.get("/orders_with_user")
def get_orders_with_user(
    order_id: int,
    db: Session = Depends(get_db)
):
    try:
        orders = crud.order.get_orders_with_user(db=db, order_id=order_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/get_order_detail")
def get_order_detail(*, db: Session = Depends(get_db), id: int) -> Any:
    try:
        order_detail = crud.order.get_order_info_detailed(db=db, id=id)
        return jsonable_encoder(order_detail)
    except Exception as e:
        logger.error(f"Error in get order detail API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.get("/get_order_id")
def get_order_id(*,id:int, db: Session = Depends(get_db)) -> Any:
    """
    Create new user.
    """
    try:
        order_id = crud.order.generate_order_id(db=db, user_id=id)
        return {"order_id": order_id}
    except Exception as e:
        logger.error(f"Error in generate order id API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.post("/shipment")
def create_bulk_shipment(order_ids: str, *, db: Session = Depends(get_db)):
    try:
        parsed_ids = map(lambda x: int(x.strip()), order_ids.split(","))
        response = map(
            lambda x: {"order_id": x, **create_shipment(x, db=db)}, parsed_ids
        )
        return list(response)
    except ValueError as e:
        return {"success": False, "error": "invalid order_id:" + str(e).split(":")[1]}


@router.post("/bulk_shipment/")
def create_bulk_shipment(ids: list[int], *, db: Session = Depends(get_db) ):
    """
    Create shipment for order
    """
    try:
        response=[]
        partner_info=PartnerInfo()
        for id in ids:
            logger.info(f"create shipment for order id : {id}")

            order = crud.order.get_order_info_detailed(db, id)
            result = crud.partner.get_shipping_estimation(db=db, order_info=order,logger=logger)
            if result: 
                partner_info.partner_id = result[0]["partner_id"]
                partner_info.amount=result[0]["total_charge"]
            
            user_id=order["users_id"]
            user_info=crud.users.get(db=db,id=user_id)
            if not user_info.wallet_balance<partner_info.amount or order["payment_type_id"]==1:

                shipment_response = crud.partner.create_partner_shipment(
                    partner_id=partner_info.partner_id, order=order, logger=logger,db=db
                )
            else:
                return HTTPException(status_code=401, detail=f"error : insufficient balance")

            order_status = crud.order_status.get_by_name(db, name="manifested")
            crud.order.update_order(db, order_in={"status_id": order_status.id}, id=id)
            user_amount_obj = crud.users.update_amount(db=db,id=order["users_id"], amount=partner_info.amount,action='minus')
            logger.info(f'Amount updated from {partner_info.amount} to {user_amount_obj.wallet_balance}')
            if not shipment_response["success"]:
                db.rollback()
                partner=[]
                partner.append(shipment_response)
                partner.append({"id":id})
                response.append(partner)
                continue
            logger.info(f" create shipment response : {shipment_response}")
            crud.order.update_order(
                db=db,
                order_in={
                    "waybill_no": shipment_response["waybill_no"],
                    "partner_id": partner_info.partner_id,
                },
                id=id,
            )
            crud.account_transaction.order_transaction(db=db, order_obj=order, partner_info= partner_info)
            db.commit()
            partner=[]
            partner.append(shipment_response)
            partner.append({"id":id})
            response.append(partner)

        return response
    except Exception as e:
        logger.error(f"Error in create shipment api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")
    
@router.post("/{id}/shipment")
def create_shipment(id: int, *, db: Session = Depends(get_db), partner_info: PartnerInfo ):
    """
    Create shipment for order
    """
    try:
        logger.info(f"create shipment for order id : {id}")
        

        order = crud.order.get_order_info_detailed(db, id)
        user_id=order["users_id"]
        user_info=crud.users.get(db=db,id=user_id)
        if not user_info.wallet_balance<partner_info.amount or order["payment_type_id"]==1:

            shipment_response = crud.partner.create_partner_shipment(
                partner_id=partner_info.partner_id, order=order, logger=logger,db=db
            )
        else:
            return HTTPException(status_code=401, detail=f"error : insufficient balance")

        order_status = crud.order_status.get_by_name(db, name="manifested")
        if partner_info.partner_id != 1:
            crud.order.update_order(db, order_in={"status_id": order_status.id}, id=id)
        else:
            crud.order.update_order(db, order_in={"status_id": 2}, id=id)

        user_amount_obj = crud.users.update_amount(db=db,id=order["users_id"], amount=partner_info.amount,action='minus')
        logger.info(f'Amount updated from {partner_info.amount} to {user_amount_obj.wallet_balance}')
        if not shipment_response["success"]:
            db.rollback()
            return shipment_response
        logger.info(f" create shipment response : {shipment_response}")
        crud.order.update_order(
            db=db,
            order_in={
                "waybill_no": shipment_response["waybill_no"],
                "partner_id": partner_info.partner_id,
            },
            id=id,
        )
        crud.account_transaction.order_transaction(db=db, order_obj=order, partner_info= partner_info)
        db.commit()
        return shipment_response
    except Exception as e:
        logger.error(f"Error in create shipment api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.post("/pickup")
def create_bulk_pickup(order_ids: str, *, db: Session = Depends(get_db)):
    try:
        parsed_ids = map(lambda x: int(x.strip()), order_ids.split(","))
        pickup_map = defaultdict[str, int](int)
        response = []
        for order_id in parsed_ids:
            order = crud.order.get_order_info_detailed(db, order_id)
            if order is None:
                response.append(
                    {
                        "order_id": order_id,
                        "success": False,
                        "error": "order doesn't exist",
                    }
                )
                continue
            key = str(order["pickup_address_id"]).ljust(3, "0")
            pickup_map[key] += len(order["product_info"])
        for warehouse, item_count in pickup_map.items():
            pickup = PickupDetail(
                pickup_date=date.today() + timedelta(days=1),
                pickup_time=time(hour=12, minute=0, second=0),
                pickup_location=warehouse,
                # FIXME: Fix quantity after order_product table join issue is fixed
                expected_package_count=item_count,
            )
            client = DelhiveryClient()
            response.append(client.raise_pickup_request(pickup))
        return response
    except ValueError as e:
        return {"success": False, "error": "invalid order_id:" + str(e).split(":")[1]}


@router.post("/{id}/pickup")
def create_pickup(
    id: int,
    *,
    data: PickupDateTime,
    db: Session = Depends(get_db),
):
    try:
        logger.info(f"pickup schedule for order id : {id}")
        order = crud.order.get_order_info_detailed(db, id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order not found: {id}")
        pickup_datetime = datetime.combine(data.pickup_date, data.pickup_time)
        adjusted_time = pickup_datetime + timedelta(hours=2)
        pickup_time_str = adjusted_time.strftime("%H:%M:%S.%f%z")
        pickup = PickupDetail(
            pickup_time=pickup_time_str,
            pickup_date=data.pickup_date,
            pickup_location=str(order["pickup_address_id"]).ljust(3, "0"),
            # FIXME: Fix quantity after order_product table join issue is fixed
            expected_package_count=len(order["product_info"]),
        )
        client = DelhiveryClient()
        response = client.raise_pickup_request(pickup)
        if not response["status"]:
            return {"success": False, "error": response["error"]}
        if not response["success"]:
            return {"success": False, "error": response["error"]["message"]}
        order_obj = crud.order.get(db=db,id=id)
        order_obj.status_id = 3
        db.commit()
        return {"success": True}
    except Exception as e:
        logger.error(f"Error in pickup schedule api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.get("/{id}/estimate")
def estimate_shipping(id: int, *, db: Session = Depends(get_db)):
    try:
        logger.info(f"estimate cost for order id : {id}")
        order = crud.order.get_order_info_detailed(db, id)
        result = crud.partner.get_shipping_estimation(db=db, order_info=order,logger=logger)
        return result
    except Exception as e:
        logger.error(f"Error in estimate shipping api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.get("/{id}/track")
def track_shipment(id: str, *, db: Session = Depends(get_db)) -> TrackingResponse:
    order = crud.order.get_order_info(db, id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order not found: {id}")
    if order["partner_name"] == "Delhivery":
        client = DelhiveryClient()
        response = client.track_shipment(order_ids=[id])
    elif order["partner_name"]=="Dtdc":
        client = DTDCClient()
        response = client.track_shipment(consignment_no=order["waybill_no"])
    elif order["partner_name"]=="Xpress":
        client=xpressClient()
        response=client.track_shipment(awb_no=order["waybill_no"])
    elif order["partner_name"]=="ecomexpress":
        client=ecomExpress()
        api_res=client.track_shipment(awb_no=order["waybill_no"])
        response=client.convert_to_tracking_response(api_res)
    elif order["partner_name"]=="maruti\n":
        client=maruti()
        response=client.track_shipment(awbNumber=order["waybill_no"])


    if response.status == 'In Transit':
        order_status = crud.order_status.get_by_name(db, name="In transit")
        crud.order.update_order(db, order_in={"status_id": order_status.id}, id=id)
        db.commit()
    elif response.status == "Delivered":
        order_status = crud.order_status.get_by_name(db, name="Delivered")
        crud.order.update_order(db, order_in={"status_id": order_status.id}, id=id)
        db.commit()
    elif response.ReverseInTransit:
        order_status = crud.order_status.get_by_name(db, name="RTO")
        crud.order.update_order(db, order_in={"status_id": order_status.id}, id=id)
        db.commit()
    response.order_date = order["date"]
    response.waybilll_no = order["waybill_no"]
    response.order_id = order["order_id"]
    return response


@router.get("/get_filtered_orders")
def get_filtered_order_detail(*, db: Session = Depends(get_db),created_by) -> Any:
    """
    This is temporary api with static status value
    """
    try:
        order_list = crud.order.get_orders_by_status(db=db,created_by=created_by)
        logger.info(f"order list {order_list}")
        result = []
        for order_id in order_list:
            # order_detail = crud.order.get_order_info_detailed(db=db, id=order_id)
            order_detail = crud.order.get_order_details(db=db,id=order_id)
            result.append(order_detail)
        return result
    except Exception as e:
        print(f"Error in get filter API :- {e}")
        logger.info(e)
        raise HTTPException(status_code=401, detail=f"error : {e}")

@router.get("/get_filtered_orders_company")
def get_filtered_order_detail(*, db: Session = Depends(get_db),created_by) -> Any:
    """
    This is temporary api with static status value
    """
    try:
        order_list = crud.order.get_orders_by_status(db=db,created_by=created_by,status=8)
        logger.info(f"order list {order_list}")
        result = []
        for order_id in order_list:
            # order_detail = crud.order.get_order_info_detailed(db=db, id=order_id)
            order_detail = crud.order.get_order_details(db=db,id=order_id)
            result.append(order_detail)
        return result
    except Exception as e:
        print(f"Error in get filter API :- {e}")
        logger.info(e)
        raise HTTPException(status_code=401, detail=f"error : {e}")

@router.get("/get_filtered_orders_new")
def get_filtered_orders(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 10,
    from_date: Annotated[Optional[date], Query(alias="from")] = None,
    to_date: Annotated[Optional[date], Query(alias="to")] = None,
    status_name: Optional[str] = None,
    status: Optional[int] = None,
    payment_type: Optional[int] = None,
    sku: Optional[str] = None,
    pickup_address_tag: Optional[str] = None,
    buyer_country: Optional[str] = None,
    order_id: Optional[str] = None,
    order_type: Optional[int] = None,
    order_type_name: Optional[str] = None,
    # sort_fields: List[Dict] = None,
) -> Any:
    """
    This is temporary api with static status value
    """
    try:
        result = crud.order.get_filtered_orders(
            db=db,
            filter_fields=locals(),
            date_from=from_date,
            date_to=to_date,
            # sort_fields=sort_fields,
            page=page,
            per_page=per_page,
        )
        return result
    except Exception as e:
        logger.error(f"Error in order save API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.post("/bulk_orders")
def bulk_order_save(*, db: Session = Depends(get_db), file: UploadFile) -> Any:
    """
    This is temporary api with static status value
    """
    try:
        order_in_list = create_order_info_from_file(file=file)
        result = []
        for order_in in order_in_list:
            try:
                db.reset()
                order = crud.order.create_order(db=db, order_in=order_in, user=test_user)
                result.append({"success": True, "data": jsonable_encoder(order)})
                db.commit()
            except Exception as e:
                result.append({"success": False, "error": str(e)})
        # print(row)
        return result
    except Exception as e:
        result.append({"success": False, "error": str(e)})


@router.get("/get_orders_by_product")
def get_order_detail_by_product(
    *, db: Session = Depends(get_db), product_id: int
) -> Any:
    """
    This is temporary api with static status value
    """
    try:
        order_list = crud.order.get_orders_by_product(db=db, product_id=product_id)
        logger.info(f"order list {order_list}")
        result = []
        for order_id in order_list:
            order_detail = crud.order.get_order_info_detailed(db=db, id=order_id)
            result.append(order_detail)
        return result
    except Exception as e:
        logger.error(f"Error in order get by product API :- {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")

@router.post("/{id}/cancel_shipment")
def cancel_shipment(id: int, *, db: Session = Depends(get_db), partner_info: CancelShipmentInfo ):

    try:
        logger.info(f"cancel shipment of order id : {id}")
        order = crud.order.get_order_info_detailed(db, id)
        cancel_response = crud.partner.cancel_partner_shipment(
                    partner_id=partner_info.partner_id, order=order, logger=logger,db=db
                )
        if cancel_response["success"]:
            order["status_id"]=4
            old_order=crud.order.get(db, id)
            crud.order.update(db,db_obj=old_order,obj_in=order)
            db.commit()
        return cancel_response
    except Exception as e:
        logger.error(f"Error in create shipment api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")


@router.put("/{order_id}")
def update_order(
    order_id: int,
    order_fields: schemas.OrderUpdate,
    db: Session = Depends(get_db),
) -> schemas.OrderCreate:
    try:
        order = crud.order.get(db=db, id=order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        update_data = order_fields.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        db.commit()
        db.refresh(order)

        return order
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")







# @router.post("/Create_Shipment")
# def create_shipment( *, shipment_details: schemas.ShipmentRequest):
#     try:
#         shipment_details = jsonable_encoder(shipment_details)
#         xpressclient = xpressClient()
#         response=xpressclient.create_shipment(shipment_data=shipment_details)
#         if response:
#             return response
        
#     except Exception as e:
#         logger.error(f"Error in creating Shipment :- {e}")
#         raise HTTPException(status_code=401,detail=f"error : {e}")

    
@router.post("/rate_calculation")
def estimate_shipping(data:dict, *, db: Session = Depends(get_db)):
    try:
        logger.info(f"estimate cost for given payyload ")
        result = crud.rate_calculation.get_shipping_estimation(db=db, data=data,logger=logger)
        return result
    except Exception as e:
        logger.error(f"Error in estimate shipping api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")
    
@router.post("/{id}/request_shipment")
def estimate_shipping(*,id:int, db: Session = Depends(get_db)):
    try:
        logger.info(f"request shipment for given id ")
        result = crud.order.get(db=db,id=id)
        result.status_id=8
        db.commit()

        return {"status":"shipment requested", "flag" : 8}
    except Exception as e:
        logger.error(f"Error in request shipping api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")

@router.get("/order/status/{order_id}", response_model=Optional[OrderStatus])
def read_order_status(order_id: int):
    """
    Retrieve order status by order ID.
    """
    db = SessionLocal()
    order_status = crud.get_order_status_by_id(db, order_id)
    db.close()
    if order_status is None:
        raise HTTPException(status_code=404, detail="Order status not found")
    return order_status
