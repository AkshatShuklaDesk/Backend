import json
import random
from sqlalchemy.orm import Session
import re
from sqlalchemy import update

import crud.order
from integrations.delhivery import DelhiveryClient
from schemas.delhivery.warehouse import CreateWarehouse
from schemas.delhivery.shipment import (
    CreateShipment,
    GetShippingCost,
)
from schemas.xpressbees import waybill
from schemas.ecomexpress.shipment import *
from schemas.maruti.shipment import MarutiOrderEstimation
from schemas.maruti.shipment import marutiAddress,LineItem,MarutiOrder
from schemas.dtdc.shipment import  Consignment, Piece
from schemas.dtdc import shipment

from integrations.dtdc import DTDCClient

from crud.order import *
from crud.base import CRUDBase
from models.partner import Partner, PartnerCreate, PartnerBase
from integrations.xpress import xpressClient
from integrations.ecomexpress import ecomExpress
from integrations.maruti import maruti


class CRUDPartner(CRUDBase[Partner, PartnerCreate, PartnerBase]):
    def get_by_name(self, db: Session, name):
        partner = db.query(self.model).filter(self.model.name == name).first()
        return partner

    def create_warehouse(self, address):
        ## Delhivery
        client = DelhiveryClient()
        warehouse = CreateWarehouse(
            name=str(address['id']).ljust(3, "0"),
            email=address['email_address'],
            phone=address['contact_no'],
            address=address['complete_address'],
            pincode=address['pincode'],
            city=address['city'],
            state=address['state'],
        )
        client.create_warehouse(warehouse)

    def create_partner_shipment(self, db: Session,partner_id, order, logger):
        if partner_id == 1:
            client = DelhiveryClient()
            shipments: list[CreateShipment] = []
            for product in order["product_info"] or []:
                shipments.append(
                    CreateShipment(
                        name=order["buyer_info"]["first_name"] or "",
                        phone=order["buyer_info"]["contact_no"] or "",
                        address=order["buyer_info"]["complete_address"] or "",
                        pincode=order["buyer_info"]["pincode"] or "",
                        payment_mode="COD"
                        if order["payment_type_id"] == 1
                        else "Prepaid",
                        order_id=str(order["id"]),
                        shipment_mode="Surface",
                        amount=str(order["total_amount"]),
                        height=str(order["height"]),
                        width=str(order["width"]),
                        weight=str(order["applicable_weight"]),
                        hsn_code=product["hsn_code"],
                        quantity="1",  # FIXME: Fix quantity after order_product table join issue is fixed
                    )
                )
            response = client.create_shipment(
                str(order["pickup_address_id"]).ljust(3, "0"), shipments
            )
            if not response["success"]:
                logger.info("Delhivery API returned error")
                logger.info(response)
                error_msg = response["rmk"]
                if response.get("packages"):
                    error_msg = response["packages"][0]["remarks"][0]
                return {"success": False, "error": error_msg}
            logger.info(f" create shipment response delhivery  : {response}")
            return {"success": True, "waybill_no": response["packages"][0]["waybill"]}
        
        elif partner_id == 2:
            origin_detail = shipment.Address(
                name=order["user_info"]["first_name"],
                pincode=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address_line_1=order["user_info"]["complete_address"],
                address_line_2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )
            destination_detail = shipment.Address(
                name=order["buyer_info"]["first_name"],
                pincode=order["buyer_info"]["pincode"],
                phone=order["buyer_info"]["contact_no"],
                address_line_1=order["buyer_info"]["complete_address"],
                address_line_2="",
                city=order["buyer_info"]["city"],
                state=order["buyer_info"]["state"],
            )

            client = DTDCClient()
            res = client.check_pincode(
                origin=origin_detail.pincode, dest=destination_detail.pincode
            )

            pieces: list[Piece] = []
            for product in order["product_info"] or []:
                pieces.append(
                    Piece(
                        description=product["name"],
                        declared_value=str(product["unit_price"]),
                        height=str(order["height"]),
                        width=str(order["width"]),
                        weight=str(order["applicable_weight"]),
                        length=str(order["length"]),
                    )
                )
            get_latest_reference_no = crud.order.get_latest_partner_order(db=db,partner_id=2)
            latest_waybill_no = get_latest_reference_no["waybill_no"]
            numeric_part = re.search(r'\d+', latest_waybill_no).group()  # Extract numeric part
            next_reference_no = "A"+str(int(numeric_part) + 1)
            consignment = Consignment(
                service_type_id="STD EXP-A",
                reference_number=str(next_reference_no),
                origin_details=origin_detail,
                destination_details=destination_detail,
                load_type="Non-Document",
                dimension_unit="cm",
                # TODO: look into this
                commodity_id="foo",
                declared_value=str(order["total_amount"]),
                consignment_type="Forward",
                cod_favor_of="",#order["buyer_info"]["first_name"] + "",
                height=str(order["height"]),
                width=str(order["width"]),
                weight=str(order["applicable_weight"]),
                length=str(order["length"]),
                # FIXME: Fix quantity after order_product table join issue is fixed
                num_pieces=str(len(pieces)),
                pieces_detail=pieces,
            )

            # if order["payment_type_id"] == 1:
            #     consignment.cod_collection_mode = "cash"
            #     consignment.cod_amount = str(order["total_amount"])
            response = client.create_shipment([consignment])[0]
            if not response.get("success", False):
                logger.info("DTDC API returned error")
                logger.info(response)
                return {"success": False, "waybill_no":None, "error": f'Error Occurred {response}'}
            return {"success": True, "waybill_no": response["reference_number"]}
        
        elif partner_id == 3:
            xpressclient = xpressClient()
            shipment_details = {}
            orderitems = []
            for product in order["product_info"]:
                orderitems.append(
                    waybill.OrderItem(
                        product_name=product["name"] if "name" in product else "",
                        product_qty=str(product["quantity"]) if "quantity" in product else "",
                        product_price=str(product["unit_price"]) if "unit_price" in product else "",
                        product_sku=product["sku"] if "sku" in product else ""
                    )
                )

            shipment_details = waybill.ShipmentRequest(
                order_number=order["order_id"] if "order_id" in order else "",
                payment_method="cod",
                consignee_name=order["buyer_info"]["first_name"] if "first_name" in order["buyer_info"] else "",
                consignee_phone=order["buyer_info"]["contact_no"] if "contact_no" in order["buyer_info"] else "",
                consignee_pincode=order["buyer_info"]["pincode"] if "pincode" in order["buyer_info"] else "",
                consignee_city=order["buyer_info"]["city"] if "city" in order["buyer_info"] else "",
                consignee_state=order["buyer_info"]["state"] if "state" in order["buyer_info"] else "",
                consignee_address=order["buyer_info"]["complete_address"] if "line1" in order["buyer_info"] else "",
                consigner_name=order["user_info"]["first_name"] if "first_name" in order["user_info"] else "",
                consigner_phone=order["user_info"]["contact_no"] if "contact_no" in order["user_info"] else "",
                consigner_pincode=order["user_info"]["pincode"] if "pincode" in order["user_info"] else "",
                consigner_city=order["user_info"]["city"] if "city" in order["user_info"] else "",
                consigner_state=order["user_info"]["state"] if "state" in order["user_info"] else "",
                consigner_address=order["user_info"]["complete_address"] if "complete_address" in order["user_info"] else "",
                consignee_gst_number="",
                consigner_gst_number="",
                pickup_location="franchise",
                products=orderitems,
                height=str(order["height"]) if "height" in order else "",
                breadth=str(order["width"]) if "width" in order else "",
                weight=str(order["applicable_weight"]) if "applicable_weight" in order else "",
                length=str(order["length"]) if "length" in order else "",
                cod_charges=order["shipping_charges"] if "shipping_charges" in order else 0,
                discount=order["discount"] if "discount" in order else 0,
                order_amount=order["sub_total"] if "sub_total" in order else 0,
                collectable_amount=order["total_amount"] if "total_amount" in order else 0,
            )
            response=xpressclient.create_shipment(shipment_data=shipment_details)
            response["success"]=response["status"]
            if response["status"]==True:
                if response["data"]:
                    response["waybill_no"]=response["data"]["awb_number"]
            if response:
                return response

        elif partner_id==4:
            ecomXpress=ecomExpress()
            waybill_res=ecomXpress.fetch_waybill()
            response_data = json.loads(waybill_res.content)
            waybill_number = response_data['awb'][0]
            shipment_details = ShipmentRequest(
                AWB_NUMBER=str(waybill_number),
                ORDER_NUMBER=order['order_id'],
                PRODUCT="COD",
                CONSIGNEE=order['buyer_info']["first_name"],
                CONSIGNEE_ADDRESS1=order['buyer_info']["complete_address"],
                DESTINATION_CITY=order['user_info']["city"],
                PINCODE=order['buyer_info']['pincode'],
                STATE=order['buyer_info']["state"],
                MOBILE=order['buyer_info']["contact_no"],
                ITEM_DESCRIPTION=order["product_info"][0]["name"],
                PIECES=order["product_info"][0]['quantity'],
                COLLECTABLE_VALUE=order["total_amount"],
                DECLARED_VALUE=order["total_amount"],
                ACTUAL_WEIGHT=order['applicable_weight'],
                VOLUMETRIC_WEIGHT=float(order["volumatric_weight"]),
                LENGTH=float(order["length"]),
                BREADTH=float(order["width"]),
                HEIGHT=float(order["height"]),
                PICKUP_NAME=order["user_info"]["first_name"],
                PICKUP_ADDRESS_LINE1=order["user_info"]["complete_address"],
                PICKUP_PINCODE=order["user_info"]["pincode"],
                PICKUP_PHONE=order["user_info"]["contact_no"],
                PICKUP_MOBILE=order["user_info"]["contact_no"],
                RETURN_NAME=order["user_info"]["first_name"],
                RETURN_ADDRESS_LINE1=order["user_info"]["complete_address"],
                RETURN_PINCODE=order["user_info"]["pincode"],
                RETURN_PHONE=order["user_info"]["contact_no"],
                RETURN_MOBILE=order["user_info"]["contact_no"],
                DG_SHIPMENT="false")
            response=ecomXpress.create_shipment(shipment_data=shipment_details)
            if not response["shipments"][0]["success"]:
                logger.info("Ecom Express API returned error")
                logger.info(response)
                return {"success": False, "waybill_no":None, "error": f'Error Occurred {response}'}
            return {"success": True, "waybill_no": waybill_number}
        
        elif partner_id==5:
            maruti_client=maruti()
            orderitems = []

            shippingAddress = marutiAddress(
                name=order["buyer_info"]["first_name"],
                zip=order["buyer_info"]["pincode"],
                phone=order["buyer_info"]["contact_no"],
                address1=order["buyer_info"]["complete_address"],
                address2="",
                city=order["buyer_info"]["city"],
                state=order["buyer_info"]["state"],
            )

            billingAddress = marutiAddress(
                name=order["user_info"]["first_name"],
                zip=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address1=order["user_info"]["complete_address"],
                address2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )

            pickupAddress = marutiAddress(
                name=order["user_info"]["first_name"],
                zip=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address1=order["user_info"]["complete_address"],
                address2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )

            returnAddress = marutiAddress(
                name=order["user_info"]["first_name"],
                zip=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address1=order["user_info"]["complete_address"],
                address2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )



            for product in order["product_info"]:
                orderitems.append(
                   LineItem(
                        name=product["name"] if "name" in product else "",
                        quantity=product["quantity"] if "quantity" in product else "",
                        price=product["unit_price"] if "unit_price" in product else "",
                        sku=product["sku"] if "sku" in product else "",
                        unitPrice=product["unit_price"] if "unit_price" in product else "",
                        weight=50
                    )
                )

            

            shipment_details = MarutiOrder(
                orderId=order["order_id"] if "order_id" in order else "",
                orderSubtype="FORWARD",
                paymentType="COD",
                currency="INR",
                lineItems=orderitems,
                shippingAddress=shippingAddress,
                billingAddress=billingAddress,
                pickupAddress=pickupAddress,
                returnAddress=returnAddress,
                width=float(order["width"]),
                amount=float(order["total_amount"]),
                deliveryPromise="SURFACE",
                products=orderitems,
                height=order["height"] if "height" in order else "",
                weight=order["applicable_weight"] * 1000 if "applicable_weight" in order else "",
                length=order["length"] if "length" in order else "",
                discount=order["discount"] if "discount" in order else 0,
                subTotal=order["sub_total"] if "sub_total" in order else 0,
            )
            response_push=maruti_client.push_order(shipment_data=shipment_details)
            if response_push["status"]==400:
                response_push["success"]=False
                return response_push
            new_order_id=response_push["data"]["orderId"]
            update(Order).filter(Order.id == order["id"]).values(order_id = new_order_id)
            if response_push["status"]==200:
                response=maruti_client.create_shipment(response=response_push)
                if response.get("error") :
                    if '{"status":500,' in response["error"]:
                        response["success"]=False
                        return response
                
                response["success"]=True
                response["waybill_no"]=response_push["data"]["awbNumber"]
                return response
            else:
                response_push["success"]=False
                return response_push

            
            

    def get_delhivery_estimations(self, order_info):
        client = DelhiveryClient()
        if not order_info:
            return {"success": False, "error": "order not found"}
        response = client.calculate_shipping(
            GetShippingCost(
                billing_mode="Express",
                status="Delivered",
                origin_pincode=order_info["user_info"]["pincode"],
                dest_pincode=order_info["buyer_info"]["pincode"],
                weight=str(order_info["applicable_weight"]),
                payment_mode="COD"
                if order_info["payment_type_id"] == 1
                else "Pre-paid",
                amount=str(order_info["total_amount"]),
            )
        )
        output = {
            "chargable_weight": response[0]["charged_weight"],
            "total_charge": response[0]["total_amount"],
            "charge_freight": 0,
            "partner_name": "Delhivery",
            "charge_type" : "Surface",
            "partner_id":1
        }
        air_output = {
            "chargable_weight": response[0]["charged_weight"],
            "total_charge": 1750,
            "charge_freight": 0,
            "partner_name": "Delhivery",
            "charge_type" : "Air",
            "partner_id":1

        }
        return output,air_output

    def get_dtdc_rate(self, order_info):
        pincode_wise_rate = {(380007, 380001): 100, (380007,380022):200, (380007,380015): 300, (380022,380051): 400}
        get_from_pincode = order_info["user_info"]["pincode"]
        get_to_pincode = order_info["buyer_info"]["pincode"]
        return pincode_wise_rate[(get_from_pincode, get_to_pincode)] if (get_from_pincode, get_to_pincode) in pincode_wise_rate.keys() else 200

    def get_xpress_rate(self,order_info):
        pincode_wise_rate = {(380007, 380001): 100, (380007,380022):200, (380007,380015): 300, (380022,380051): 400}
        get_from_pincode = order_info["user_info"]["pincode"]
        get_to_pincode = order_info["buyer_info"]["pincode"]
        return pincode_wise_rate[(get_from_pincode, get_to_pincode)] if (get_from_pincode, get_to_pincode) in pincode_wise_rate.keys() else 200

    def get_ecomexpress_rate(self,order_info):
        pincode_wise_rate = {(380007, 380001): 100, (380007,380022):200, (380007,380015): 300, (380022,380051): 400}
        get_from_pincode = order_info["user_info"]["pincode"]
        get_to_pincode = order_info["buyer_info"]["pincode"]
        return pincode_wise_rate[(get_from_pincode, get_to_pincode)] if (get_from_pincode, get_to_pincode) in pincode_wise_rate.keys() else 200
    
    def get_dtdc_estimations(self, order_info):
        response = {}
        rate = self.get_dtdc_rate(order_info=order_info)
        response = {
            "chargable_weight": order_info["applicable_weight"],
            "total_charge": rate,
            "charge_freight": 0,
            "charge_type" : "Surface",
            "partner_name": "DTDC",
            "partner_id":2
        }
        air_response = {
            "chargable_weight": order_info["applicable_weight"],
            "total_charge": 1300,
            "charge_freight": 0,
            "partner_name": "DTDC",
            "charge_type" : "Air",
            "partner_id":2
        }
        return response,air_response
    def get_xpress_estimations(self,order_info):
        response={}
        client=xpressClient()
        order_info=waybill.XpressEstimation(
            origin=int(order_info["user_info"]["pincode"]),
            destination=int(order_info["buyer_info"]["pincode"]),
            payment_type="cod",
            order_amount=order_info["total_amount"],
            weight=int(order_info["applicable_weight"]),
            length=int(order_info["length"]) if order_info["length"] is not None else 0,
            breadth=int(order_info["width"]) if order_info["width"] is not None else 0,
            height=int(order_info["height"]) if order_info["height"] is not None else 0
        )
        rate=client.calculate_shipping(order_info=order_info)
        if rate["status"]:

            response={
                "chargable_weight": rate["data"][0]["chargeable_weight"],
                "total_charge": rate["data"][0]["total_charges"],
                "charge_freight": rate["data"][0]["freight_charges"],
                "partner_name": "Xpressbees",
                "charge_type" : "Surface",
                "partner_id":3
            }
            air_response = {
                  "chargable_weight": rate["data"][4]["chargeable_weight"],
                "total_charge": rate["data"][4]["total_charges"],
                "charge_freight": rate["data"][4]["freight_charges"],
                "partner_name": "Xpressbees",
                "charge_type" : "Air",
                "partner_id":3
            }
            return response,air_response
        else:
            return rate
    
    def get_ecomexpress_estimations(self,order_info):
        ecom = ecomExpress()
        order_info=OrderEstimation(
            orginPincode=int(order_info["user_info"]["pincode"]),
            destinationPincode=order_info["buyer_info"]["pincode"],
            productType="ppd",
            chargeableWeight=order_info["applicable_weight"],
            codAmount=0
        )
        response = ecom.rate_calculation(order=order_info)
        output={
            "total_charge": response[0]["chargesBreakup"]['total_charge'],
            "charge_freight": 0,
            "partner_name": "ECOM EXPRESS",
            "charge_type" : "Surface",
            "partner_id":4
        }
        air_output = {
            "total_charge": 1950,
            "charge_freight": 0,
            "partner_name": "ECOM EXPRESS",
            "charge_type": "Air",
            "partner_id":4
        }
        return output,air_output
    
    def get_maruti_estimations(self,order_info):
        travel_type=["SURFACE","AIR"]
        maruti_express=maruti()
        estimation=[]

        for mode in travel_type:

            order=MarutiOrderEstimation(
                fromPincode=int(order_info["user_info"]["pincode"]),
                toPincode=int(order_info["buyer_info"]["pincode"]),
                deliveryPromise=mode,
                weight=order_info["applicable_weight"],
                width=order_info["width"],
                height=order_info["height"],
                length=order_info["length"]
            )

            esti=maruti_express.rate_calculation(order=order)
            esti=jsonable_encoder(esti)
            estimation.append(esti)
        response_surface={}
        response_surface["total_charge"]=estimation[0]["data"]["shippingCharge"]
        response_surface["chargable_weight"]=estimation[0]["data"]["appliedZone"]["Weight"]
        response_surface["charge_type"]=estimation[0]["data"]["appliedZone"]["TravelType"]
        response_surface["partner_name"]="Maruti"
        response_surface["charge_freight"]=estimation[0]["data"]["appliedZone"]["FreightCharge"]
        response_surface["partner_id"]=5

        response_air={}
        response_air["total_charge"]=estimation[1]["data"]["shippingCharge"]
        response_air["chargable_weight"]=estimation[1]["data"]["appliedZone"]["Weight"]
        response_air["charge_type"]=estimation[1]["data"]["appliedZone"]["TravelType"]
        response_air["partner_name"]="Maruti"
        response_air["charge_freight"]=estimation[1]["data"]["appliedZone"]["FreightCharge"]
        response_surface["partner_id"]=5


        return response_surface,response_air

    def get_sorted_estimations(self, all_estimations):
        sorted_estimations = sorted(all_estimations, key=lambda d: d["total_charge"])
        return sorted_estimations

    def get_shipping_estimation(self, db: Session, order_info,logger):
        all_estimations = []
        delivery_partners = [
        ("Delhivery", self.get_delhivery_estimations),
        ("DTDC", self.get_dtdc_estimations),
        ("XpressBees", self.get_xpress_estimations),
        ("EcomExpress", self.get_ecomexpress_estimations),
        ("Maruti", self.get_maruti_estimations)
    ]

        for partner_name, estimation_func in delivery_partners:
            try:
                surface_estimation, air_estimation = estimation_func(order_info=order_info)
                all_estimations.extend([surface_estimation, air_estimation])
            except Exception as e:
                logger.info(f"Error estimating shipping with {partner_name}: {str(e)}")


        sorted_estimations = self.get_sorted_estimations(all_estimations)
        return sorted_estimations
    

    def cancel_partner_shipment(self,db:Session,partner_id,order,logger):
        if partner_id== 1:
            client=DelhiveryClient()
            awb_number=order["waybill_no"]
            response=client.cancel_shipment(waybill=awb_number)
            if response["status"]=="Failure":
                response["success"]=False
            else:
                response["success"]=True
            return response
        elif partner_id==2:
            client=DTDCClient()
            awb_number=order["waybill_no"]

            return None
        elif partner_id==3:
            client=xpressClient()
            awb_number=order["waybill_no"]
            response=client.cancel_shipment(awb_number)
            return response
        elif partner_id== 4:
            client=ecomExpress()
            awb_number=order["waybill_no"]
            response=client.cancel_shipment(awb_number)
            print(response)
            response[0]["partner_name"]="Ecom Express"
            if not response[0]["success"]:
                if response[0]["reason"]=='Shipment Cannot Be Cancelled As RTO Lock Already Applied':
                    old_order=crud.order.get(db,id=order["id"])
                    order["status_id"]=7
                    crud.order.update(db,db_obj=old_order,obj_in=order)
                    db.commit()
                logger.info("Ecom Express shipment cancellation failed")
                logger.info(response)
                return {"success": False, "awb_number":awb_number, "error": f'Error Occurred {response}'}
            logger.info("Ecom Express shipment cancellation done")
            return {"success": True, "awb_number": awb_number}
        elif partner_id== 5:
            client=maruti()
            order_id=order["order_id"]
            response=client.cancel_shipment(order_id)
            response_content_str = response.decode('utf-8')

            # Parse the JSON response
            response_data = json.loads(response_content_str)

            # Check if the order status is "CANCELED"
            if response_data.get("status") == 400 and "order status is CANCELED" in response_data.get("message", ""):
                res={"success":False,"error":response}
                return res
                # If you want to return the response, you can return it here
            else:

                print(response)
                response_data["partner_name"]="Maruti"
                if not response_data["status"]==200:
                    logger.info("maruti shipment cancellation failed")
                    logger.info(response)
                    return {"success": False, "awb_number":order["waybill_no"], "error": f'Error Occurred {response}'}
                logger.info("Ecom Express shipment cancellation done")
                return {"success": True, "awb_number": order["waybill_no"]}
            
    def create_return_shipment(self, db: Session, partner_id,order, logger):
        
        if partner_id == 1:
            client = DelhiveryClient()
            shipments: list[CreateShipment] = []
            for product in order["product_info"] or []:
                shipments.append(
                    CreateShipment(
                        name=order["buyer_info"]["first_name"] or "",
                        phone=order["buyer_info"]["contact_no"] or "",
                        address=order["buyer_info"]["complete_address"] or "",
                        pincode=order["buyer_info"]["pincode"] or "",
                        payment_mode="COD"
                        if order["payment_type_id"] == 1
                        else "Prepaid",
                        order_id=str(order["id"]),
                        shipment_mode="Surface",
                        amount=str(order["total_amount"]),
                        height=str(order["height"]),
                        width=str(order["width"]),
                        weight=str(order["applicable_weight"]),
                        hsn_code=product["hsn_code"],
                        quantity="1",  # FIXME: Fix quantity after order_product table join issue is fixed
                    )
                )
            response = client.create_shipment(
                str(order["pickup_address_id"]).ljust(3, "0"), shipments
            )
            if not response["success"]:
                logger.info("Delhivery API returned error")
                logger.info(response)
                error_msg = response["rmk"]
                if response.get("packages"):
                    error_msg = response["packages"][0]["remarks"][0]
                return {"success": False, "error": error_msg}
            logger.info(f" create shipment response delhivery  : {response}")
            return {"success": True, "waybill_no": response["packages"][0]["waybill"]}
        elif partner_id == 2:
            origin_details = Address(
                name=order["user_info"]["first_name"],
                pincode=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address_line_1=order["user_info"]["complete_address"],
                address_line_2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )
            destination_details = Address(
                name=order["buyer_info"]["first_name"],
                pincode=order["buyer_info"]["pincode"],
                phone=order["buyer_info"]["contact_no"],
                address_line_1=order["buyer_info"]["complete_address"],
                address_line_2="",
                city=order["buyer_info"]["city"],
                state=order["buyer_info"]["state"],
            )

            client = DTDCClient()
            res = client.check_pincode(
                origin=origin_details.pincode, dest=destination_details.pincode
            )

            pieces: list[Piece] = []
            for product in order["product_info"] or []:
                pieces.append(
                    Piece(
                        description=product["name"],
                        declared_value=str(product["unit_price"]),
                        height=str(order["height"]),
                        width=str(order["width"]),
                        weight=str(order["applicable_weight"]),
                        length=str(order["length"]),
                    )
                )
            get_latest_reference_no = crud.order.get_latest_partner_order(db=db,partner_id=2)
            latest_waybill_no = get_latest_reference_no["waybill_no"]
            numeric_part = re.search(r'\d+', latest_waybill_no).group()  # Extract numeric part
            next_reference_no = "A"+str(int(numeric_part) + 1)
            consignment = Consignment(
                service_type_id="STD EXP-A",
                reference_number=str(next_reference_no),
                origin_details=origin_details,
                destination_details=destination_details,
                load_type="Non-Document",
                dimension_unit="cm",
                # TODO: look into this
                commodity_id="foo",
                declared_value=str(order["total_amount"]),
                consignment_type="Forward",
                cod_favor_of="",#order["buyer_info"]["first_name"] + "",
                height=str(order["height"]),
                width=str(order["width"]),
                weight=str(order["applicable_weight"]),
                length=str(order["length"]),
                # FIXME: Fix quantity after order_product table join issue is fixed
                num_pieces=str(len(pieces)),
                pieces_detail=pieces,
            )

            # if order["payment_type_id"] == 1:
            #     consignment.cod_collection_mode = "cash"
            #     consignment.cod_amount = str(order["total_amount"])
            response = client.create_shipment([consignment])[0]
            if not response.get("success", False):
                logger.info("DTDC API returned error")
                logger.info(response)
                return {"success": False, "waybill_no":None, "error": f'Error Occurred {response}'}
            return {"success": True, "waybill_no": response["reference_number"]}
        
        elif partner_id == 3:
            xpressclient = xpressClient()
            shipment_details = {}
            orderitems = []
            for product in order["product_info"]:
                orderitems.append(
                    waybill.OrderItem(
                        product_name=product["name"] if "name" in product else "",
                        product_qty=str(product["quantity"]) if "quantity" in product else "",
                        product_price=str(product["unit_price"]) if "unit_price" in product else "",
                        product_sku=product["sku"] if "sku" in product else ""
                    )
                )

            shipment_details = waybill.ShipmentReturn(
                order_number=order["order_id"] if "order_id" in order else "",
                payment_method="cod",
                consignee_name=order["buyer_info"]["first_name"] if "first_name" in order["buyer_info"] else "",
                consignee_phone=order["buyer_info"]["contact_no"] if "contact_no" in order["buyer_info"] else "",
                consignee_pincode=order["buyer_info"]["pincode"] if "pincode" in order["buyer_info"] else "",
                consignee_city=order["buyer_info"]["city"] if "city" in order["buyer_info"] else "",
                consignee_state=order["buyer_info"]["state"] if "state" in order["buyer_info"] else "",
                consignee_address=order["buyer_info"]["complete_address"] if "line1" in order["buyer_info"] else "",
                consigner_name=order["user_info"]["first_name"] if "first_name" in order["user_info"] else "",
                consigner_phone=order["user_info"]["contact_no"] if "contact_no" in order["user_info"] else "",
                consigner_pincode=order["user_info"]["pincode"] if "pincode" in order["user_info"] else "",
                consigner_city=order["user_info"]["city"] if "city" in order["user_info"] else "",
                consigner_state=order["user_info"]["state"] if "state" in order["user_info"] else "",
                consigner_address=order["user_info"]["complete_address"] if "complete_address" in order["user_info"] else "",
                consignee_gst_number="",
                consigner_gst_number="",
                pickup_location="franchise",
                products=orderitems,
                height=str(order["height"]) if "height" in order else "",
                breadth=str(order["width"]) if "width" in order else "",
                weight=str(order["applicable_weight"]) if "applicable_weight" in order else "",
                length=str(order["length"]) if "length" in order else "",
                cod_charges=order["shipping_charges"] if "shipping_charges" in order else 0,
                discount=order["discount"] if "discount" in order else 0,
                order_amount=order["sub_total"] if "sub_total" in order else 0,
                collectable_amount=order["total_amount"] if "total_amount" in order else 0,
            )
            response=xpressclient.return_shipment(shipment_data=shipment_details)
            response["success"]=response["status"]
            response["waybill_no"]=response["data"]["awb_number"]
            if response:
                return response

        elif partner_id==4:
            ecomXpress=ecomExpress()
            # waybill_res=ecomXpress.fetch_waybill()
            # response_data = json.loads(waybill_res.content)
            # waybill_number = response_data['awb'][0]
            shipment_details = ShipmentReturn(
                # AWB_NUMBER=str(waybill_number),
                AWB_NUMBER=order["waybill_no"],
                ORDER_NUMBER=order['order_id'],
                PRODUCT="COD",
                REVPICKUP_NAME=order['buyer_info']["first_name"],
                REVPICKUP_ADDRESS1=order['buyer_info']["complete_address"],
                DESTINATION_CITY=order['user_info']["city"],
                REVPICKUP_PINCODE=order['buyer_info']['pincode'],
                REVPICKUP_STATE=order['buyer_info']["state"],
                REVPICKUP_MOBILE=order['buyer_info']["contact_no"],
                ITEM_DESCRIPTION=order["product_info"][0]["name"],
                PIECES=str(order["product_info"][0]['quantity']),
                COLLECTABLE_VALUE=str(order["total_amount"]),
                DECLARED_VALUE=str(order["total_amount"]),
                ACTUAL_WEIGHT=str(order['applicable_weight']),
                VOLUMETRIC_WEIGHT=str(order["volumatric_weight"]),
                LENGTH=str(order["length"]),
                BREADTH=str(order["width"]),
                HEIGHT=str(order["height"]),
                DG_SHIPMENT="false",
                )
            
            shipment_info=EcomexpressObjectsReturn(
                SHIPMENT=shipment_details
            )
            response=ecomXpress.return_shipment(shipment_data=shipment_info)
            if not response["RESPONSE-OBJECTS"]["AIRWAYBILL-OBJECTS"]["AIRWAYBILL"]["success"]:
                logger.info("Ecom Express API returned error")
                logger.info(response)
                return {"success": False, "waybill_no":None, "error": f'Error Occurred {response}'}
            return {"success": True, "waybill_no": order["waybill_no"]}
        
        elif partner_id==5:
            maruti_client=maruti()
            orderitems = []

            shippingAddress = shipment.Address(
                name=order["buyer_info"]["first_name"],
                zip=order["buyer_info"]["pincode"],
                phone=order["buyer_info"]["contact_no"],
                address1=order["buyer_info"]["complete_address"],
                address2="",
                city=order["buyer_info"]["city"],
                state=order["buyer_info"]["state"],
            )

            billingAddress = shipment.Address(
                name=order["user_info"]["first_name"],
                zip=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address1=order["user_info"]["complete_address"],
                address2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )

            pickupAddress = shipment.Address(
                name=order["user_info"]["first_name"],
                zip=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address1=order["user_info"]["complete_address"],
                address2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )

            returnAddress = shipment.Address(
                name=order["user_info"]["first_name"],
                zip=order["user_info"]["pincode"],
                phone=order["user_info"]["contact_no"],
                address1=order["user_info"]["complete_address"],
                address2="",
                city=order["user_info"]["city"],
                state=order["user_info"]["state"],
            )



            for product in order["product_info"]:
                orderitems.append(
                    shipment.LineItem(
                        name=product["name"] if "name" in product else "",
                        quantity=product["quantity"] if "quantity" in product else 0,
                        price=int(product["unit_price"]) if "unit_price" in product else 0,
                        sku=product["sku"] if "sku" in product else "",
                        unitPrice=int(product["unit_price"]) if "unit_price" in product else 0,
                        weight=50
                    )
                )

            

            shipment_details = shipment.Order(
                orderId=order["order_id"] if "order_id" in order else "",
                orderSubtype="REVERSE",
                paymentType="COD",
                currency="INR",
                lineItems=orderitems,
                shippingAddress=shippingAddress,
                billingAddress=billingAddress,
                pickupAddress=pickupAddress,
                returnAddress=returnAddress,
                width=float(order["width"]),
                amount=float(order["total_amount"]),
                deliveryPromise="SURFACE",
                products=orderitems,
                height=order["height"] if "height" in order else "",
                weight=order["applicable_weight"] if "applicable_weight" in order else "",
                length=order["length"] if "length" in order else "",
                discount=order["discount"] if "discount" in order else 0,
                subTotal=order["sub_total"] if "sub_total" in order else 0,
            )
            response_push=maruti_client.push_order(shipment_data=shipment_details)
            if response_push["status"]==400:
                response_push["success"]=False
                return response_push
            new_order_id=response_push["data"]["orderId"]
            update(Order).filter(Order.id == order["id"]).values(order_id = new_order_id)
            if response_push["status"]==200:
                response=maruti_client.create_shipment(response=response_push)
                if response.get("error") :
                    if '{"status":500,' in response["error"]:
                        response["success"]=False
                        return response
                
                response["success"]=True
                response["waybill_no"]=response_push["data"]["awbNumber"]
                return response
            else:
                response_push["success"]=False
                return response_push

partner = CRUDPartner(Partner)
