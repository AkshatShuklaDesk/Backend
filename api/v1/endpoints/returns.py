from collections import defaultdict
from datetime import date, time, timedelta
from typing import Annotated, Any, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, Query, UploadFile,HTTPException
from sqlmodel import Session
import crud
import schemas
from schemas.common import TrackingResponse,PartnerInfo,CancelShipmentInfo

import traceback
from integrations.delhivery import DelhiveryClient
from api.deps import get_db
from schemas.delhivery.shipment import CreateShipment, GetShippingCost, PickupDateTime, PickupDetail
from core.logging_utils import setup_logger
import logging
from scripts.order import create_order_info_from_file

# this is temporary till user auth flow gets implemented
from temp import test_user

log_name = "return"
endpoint_device_logger_setup = setup_logger(log_name, level='INFO')
logger = logging.getLogger(log_name)

router = APIRouter()


@router.post("/")
def create_return(
    *,
    db: Session = Depends(get_db),
    user_id : int,
    return_in: schemas.ReturnCreate,
) -> Any:
    """
        Create new return.
    """
    try:
        logger.info(f'create return args : {jsonable_encoder(return_in)}')
        return_order = crud.returns.create_return(db=db, return_in=return_in,user=user_id,logger=logger)
        result = jsonable_encoder(return_order)
        db.commit()
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Error in order save API :- {e}")
        raise HTTPException(status_code=401, detail=f'error : {e}')


@router.put("/")
def update_return(
    *,
    db: Session = Depends(get_db),
    return_in: schemas.ReturnUpdate,
    id: int,
    user_id : int
) -> Any:
    """
    Create new user.
    """
    try:
        logger.info(f'update return args for id {id} :- {jsonable_encoder(return_in)}')
        return_in = return_in.model_dump(exclude_unset=True)
        updated_return = crud.returns.update_return(db=db, return_in=return_in,id=id,user=user_id)
        result = { 'data': updated_return }
        db.commit()
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.info(f'Error in order update API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.get("/get_return_detail")
def get_return_detail(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    """
    Create new user.
    """
    try:
        return_detail = crud.returns.get_return_info_detailed(db=db,id=id)
        return jsonable_encoder(return_detail)
    except Exception as e:
        logger.error(f'Error in get order detail API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.get("/get_return_id")
def get_return_id(
    *,
    db: Session = Depends(get_db),
    user_id : int
) -> Any:
    """
    Create new user.
    """
    try:
        return_id = crud.returns.generate_return_id(db=db,user_id=user_id)
        return { "return_id": return_id }
    except Exception as e:
        logger.error(f'Error in generate order id API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.post("/shipment")
def create_bulk_shipment(
    order_ids: str,
    *,
    db: Session = Depends(get_db)
):
    try:
        parsed_ids = map(lambda x: int(x.strip()), order_ids.split(","))
        response = map(lambda x: { "order_id": x, **create_shipment(x, db=db) }, parsed_ids)
        return list(response)
    except ValueError as e:
        logger.error(traceback.format_exc())
        return { "success": False, "error": "invalid order_id:" + str(e).split(":")[1] }

@router.post("/{id}/shipment")
def create_shipment(
    id: int,
    *,
    db: Session = Depends(get_db),
    partner_info: PartnerInfo
):
    """
    Create shipment for order
    """
    try:
        logger.info(f'create shipment for order id : {id}')
        returns = crud.returns.get_return_info_detailed(db, id)

        shipment_response = crud.partner.create_return_shipment(
            order=returns, logger=logger,db=db,partner_id=partner_info.partner_id
        )
        if shipment_response["success"]:
            db.commit()
            return_status = crud.returns_status.get_by_name(db, name="manifested")
            crud.returns.update_return(db, return_in={ "status_id": return_status.id }, id=id)
            return { "success": True }
        else:
            return {"success":False,"error":shipment_response}
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'Error in create shipment api : {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.post("/pickup")
def create_bulk_pickup(
    return_ids: str,
    *,
    db: Session = Depends(get_db)
):
    try:
        parsed_ids = map(lambda x: int(x.strip()), return_ids.split(","))
        pickup_map = defaultdict[str, int](int)
        response = []
        for order_id in parsed_ids:
            order = crud.returns.get_return_info_detailed(db, order_id)
            if order is None:
                response.append({ "order_id": order_id, "success": False, "error": "order doesn't exist" })
                continue
            key = str(order["pickup_address_id"]).ljust(3, '0')
            # FIXME: Fix quantity after order_product table join issue is fixed
            pickup_map[key] += len(order["product_info"])
        for warehouse, item_count in pickup_map.items():
            pickup = PickupDetail(
                pickup_date=date.today() + timedelta(days=1),
                pickup_time=time(hour=12, minute=0, second=0),
                pickup_location=warehouse,
                expected_package_count=item_count
            )
            client = DelhiveryClient()
            response.append(client.raise_pickup_request(pickup))
        return response
    except ValueError as e:
        return { "success": False, "error": "invalid order_id:" + str(e).split(":")[1] }

@router.post("/{id}/pickup")
def create_pickup(
    id: int,
    *,
    data: PickupDateTime,
    db: Session = Depends(get_db),
):
    try:
        logger.info(f'pickup schedule for order id : {id}')
        return_data = crud.returns.get_return_info_detailed(db, id)
        pickup = PickupDetail(
            pickup_time=data.pickup_time,
            pickup_date=data.pickup_date,
            pickup_location=str(return_data["pickup_address_id"]).ljust(3, '0'),
            # FIXME: Fix quantity after order_product table join issue is fixed
            expected_package_count=len(return_data["product_info"])
        )
        client = DelhiveryClient()
        response = client.raise_pickup_request(pickup)
        if not response["status"]:
            return {
                "success": False,
                "error": response["error"]
            }
        if not response["success"]:
            return {
                "success": False,
                "error": response["error"]["message"]
            }
        return { "success": True }
    except Exception as e:
        logger.error(f'Error in pickup schedule api : {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.get("/{id}/estimate")
def estimate_shipping(id: int, *, db: Session = Depends(get_db)):
   
    try:
        logger.info(f"estimate cost for order id : {id}")
        order = crud.returns.get_return_info_detailed(db, id)
        result = crud.partner.get_shipping_estimation(db=db, order_info=order)
        return result
    except Exception as e:
        logger.error(f"Error in estimate shipping api : {e}")
        raise HTTPException(status_code=401, detail=f"error : {e}")

@router.get("/track")
def track_shipment(
    return_id: Optional[str] = None,
    waybill_no: Optional[str] = None,
    *,
    db: Session = Depends(get_db)
):
#     return {
#             "ShipmentData": [
#                 {
#                     "Shipment": {
#                         "CourierName": "Delhivery",
#                         "PickUpDate": "2023-12-26T15:27:45.469",
#                         "Destination": "",
#                         "DestRecieveDate": None,
#                         "Scans": [
#                             {
#                                 "ScanDetail": {
#                                     "ScanDateTime": "2023-12-26T15:27:46.348",
#                                     "ScanType": "UD",
#                                     "Scan": "Manifested",
#                                     "StatusDateTime": "2023-12-26T15:27:46.348",
#                                     "ScannedLocation": "Ahmedabad_Thaltej_C (Gujarat)",
#                                     "StatusCode": "X-UCI",
#                                     "Instructions": "Manifest uploaded"
#                                     }
#                                 }
#                             ],
#                         "Status": {
#                             "Status": "Manifested",
#                             "StatusLocation": "Ahmedabad_Thaltej_C (Gujarat)",
#                             "StatusDateTime": "2023-12-26T15:27:46.348",
#                             "RecievedBy": "",
#                             "StatusCode": "X-UCI",
#                             "StatusType": "UD",
#                             "Instructions": "Manifest uploaded"
#                             },
#                         "ReturnPromisedDeliveryDate": None,
#                         "Ewaybill": [],
#                         "InvoiceAmount": 100,
#                         "ChargedWeight": None,
#                         "PickedupDate": None,
#                         "DeliveryDate": None,
#                         "SenderName": "cface8-BEUTOPIANTECHNOSOFTP-do",
#                         "AWB": "26949910000011",
#                         "DispatchCount": 0,
#                         "OrderType": "Pre-paid",
#                         "ReturnedDate": None,
#                         "ExpectedDeliveryDate": None,
#                         "RTOStartedDate": None,
#                         "Extras": "",
#                         "FirstAttemptDate": None,
#                         "ReverseInTransit": False,
#                         "Quantity": "1",
#                         "Origin": "Ahmedabad_Thaltej_C (Gujarat)",
#                         "Consignee": {
#                             "City": "",
#                             "Name": "Meet",
#                             "Address1": [],
#                             "Address2": [],
#                             "Address3": "",
#                             "PinCode": 380007,
#                             "State": "Gujarat",
#                             "Telephone2": "",
#                             "Country": "India",
#                             "Telephone1": ""
#                             },
#         "ReferenceNo": "15",
#         "OutDestinationDate": None,
#         "CODAmount": 0,
#         "PromisedDeliveryDate": None,
#         "PickupLocation": "105",
#         "OriginRecieveDate": None,
#         "OrderDate": "2023-12-26T06:25:35.125000"
#       }
#     }
#   ]
# }
    if not return_id and not waybill_no:
        return {
            "success": False,
            "message": "order_id or waybill_no is required"
        }
    client = DelhiveryClient()
    order_ids = [return_id] if return_id else []
    waybills = [waybill_no] if waybill_no else []
    response = client.track_shipment(order_ids=order_ids, waybills=waybills)
    for shipment in response.get("ShipmentData", []):
        returns = crud.returns.get_return_info(db, shipment["Shipment"]["ReferenceNo"])
        shipment["Shipment"]["CourierName"] = returns["partner_name"]
        shipment["Shipment"]["OrderDate"] = returns["date"]
    return response

@router.get("/get_filtered_returns")
def get_filtered_returns(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 10,
    from_date: Annotated[Optional[date], Query(alias="from")] = None,
    to_date: Annotated[Optional[date], Query(alias="to")] = None,
    status_name: Optional[str] = None,
    status: Optional[int] = None,
    sku: Optional[str] = None,
    pickup_address_tag: Optional[str] = None,
    buyer_country: Optional[str] = None,
    return_id: Optional[str] = None,
    return_reason: Optional[int] = None,
    return_reason_name: Optional[str] = None,
    user_id : int
    # sort_fields: List[Dict] = None,

) -> Any:
    """
    This is temporary api with static status value
    """
    try:
        result = crud.returns.get_filtered_returns(
            db=db,
            filter_fields=locals(),
            date_from=from_date,
            date_to=to_date,
            page=page,
            per_page=per_page,
            user_id = user_id
            # sort_fields=sort_fields,
        )
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'Error in order save API :- {e}')
        raise HTTPException(status_code=401, detail=f'error : {e}')

@router.post("/bulk_orders")
def bulk_order_save(
    *,
    db: Session = Depends(get_db),
    file: UploadFile
) -> Any:
    """
    This is temporary api with static status value
    """
    order_in_list = create_order_info_from_file(file=file)
    result = []
    for order_in in order_in_list:
        try:
            db.reset()
            order = crud.order.create_order(db=db,order_in=order_in,user=test_user)
            result.append({ "success": True, "data": jsonable_encoder(order) })
            db.commit()
        except Exception as e:
            result.append({ "success": False, "error": str(e) })
        # print(row)
    return result
