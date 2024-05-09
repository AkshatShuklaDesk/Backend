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
from schemas.maruti import shipment

from schemas.dtdc.shipment import Address, Consignment, Piece
from integrations.dtdc import DTDCClient

from crud.order import *
from crud.base import CRUDBase
from models.partner import Partner, PartnerCreate, PartnerBase
from integrations.xpress import xpressClient
from integrations.ecomexpress import ecomExpress
from integrations.maruti import maruti


class CRUDRate(CRUDBase[Partner, PartnerCreate, PartnerBase]):

    def get_delhivery_estimations(self, order_info):
            client = DelhiveryClient()
            if not order_info:
                return {"success": False, "error": "order not found"}
            response = client.calculate_shipping(
                GetShippingCost(
                    billing_mode="Express",
                    status="Delivered",
                    origin_pincode=order_info["pickup_pincode"],
                    dest_pincode=order_info["delivery_pincode"],
                    weight=str(order_info["weight"]),
                    payment_mode="COD"
                    if order_info["payment_type_id"] == 1
                    else "Pre-paid",
                    amount=str(order_info["shipment_value"]),
                )
            )
            output = {
                "chargable_weight": response[0]["charged_weight"],
                "total_charge": response[0]["total_amount"],
                "charge_freight": 0,
                "partner_name": "Delhivery",
                "charge_type" : "Surface"
            }
            air_output = {
                "chargable_weight": response[0]["charged_weight"],
                "total_charge": 1750,
                "charge_freight": 0,
                "partner_name": "Delhivery",
                "charge_type" : "Air"
            }
            return output,air_output

    def get_dtdc_rate(self, order_info):
        pincode_wise_rate = {(380007, 380001): 100, (380007,380022):200, (380007,380015): 300, (380022,380051): 400}
        get_from_pincode = order_info["pickup_pincode"]
        get_to_pincode = order_info["delivery_pincode"]
        return pincode_wise_rate[(get_from_pincode, get_to_pincode)] if (get_from_pincode, get_to_pincode) in pincode_wise_rate.keys() else 200

    def get_xpress_rate(self,order_info):
        pincode_wise_rate = {(380007, 380001): 100, (380007,380022):200, (380007,380015): 300, (380022,380051): 400}
        get_from_pincode = order_info["pickup_pincode"]
        get_to_pincode = order_info["delivery_pincode"]
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
            "chargable_weight": order_info["weight"],
            "total_charge": rate,
            "charge_freight": 0,
            "charge_type" : "Surface",
            "partner_name": "DTDC",
        }
        air_response = {
            "chargable_weight": order_info["weight"],
            "total_charge": 1300,
            "charge_freight": 0,
            "partner_name": "DTDC",
            "charge_type" : "Air"
        }
        return response,air_response
    def get_xpress_estimations(self,order_info):
        response={}
        client=xpressClient()
        order_info=waybill.XpressEstimation(
            origin=order_info["pickup_pincode"],
            destination=order_info["delivery_pincode"],
            payment_type="cod",
            order_amount=order_info["shipment_value"],
            weight=int(order_info["weight"]),
            length=int(order_info["length"]),
            breadth=int(order_info["width"]),
            height=int(order_info["height"])
        )
        rate=client.calculate_shipping(order_info=order_info)
        if rate["status"]:
            response={
                "chargable_weight": rate["data"][0]["chargeable_weight"],
                "total_charge": rate["data"][0]["total_charges"],
                "charge_freight": rate["data"][0]["freight_charges"],
                "partner_name": "Xpressbees",
                "charge_type" : "Surface"
            }
            air_response = {
                  "chargable_weight": rate["data"][4]["chargeable_weight"],
                "total_charge": rate["data"][4]["total_charges"],
                "charge_freight": rate["data"][4]["freight_charges"],
                "partner_name": "Xpressbees",
                "charge_type" : "Air"
            }
            return response,air_response
        else:
            return rate
    
    def get_ecomexpress_estimations(self,order_info):
        ecom = ecomExpress()
        order_info=OrderEstimation(
            orginPincode=int(order_info["pickup_pincode"]),
            destinationPincode=order_info["delivery_pincode"],
            productType="ppd",
            chargeableWeight=order_info["weight"],
            codAmount=0
        )
        response = ecom.rate_calculation(order=order_info)
        output={
            "total_charge": response[0]["chargesBreakup"]['total_charge'],
            "charge_freight": 0,
            "partner_name": "ECOM EXPRESS",
            "charge_type" : "Surface"
        }
        air_output = {
            "total_charge": 1950,
            "charge_freight": 0,
            "partner_name": "ECOM EXPRESS",
            "charge_type": "Air",
        }
        return output,air_output
    
    def get_maruti_estimations(self,order_info):
        travel_type=["SURFACE","AIR"]
        maruti_express=maruti()
        estimation=[]

        for mode in travel_type:

            order=shipment.MarutiOrderEstimation(
                fromPincode=int(order_info["pickup_pincode"]),
                toPincode=int(order_info["delivery_pincode"]),
                deliveryPromise=mode,
                weight=order_info["weight"],
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

        response_air={}
        response_air["total_charge"]=estimation[1]["data"]["shippingCharge"]
        response_air["chargable_weight"]=estimation[1]["data"]["appliedZone"]["Weight"]
        response_air["charge_type"]=estimation[1]["data"]["appliedZone"]["TravelType"]
        response_air["partner_name"]="Maruti"
        response_air["charge_freight"]=estimation[1]["data"]["appliedZone"]["FreightCharge"]
        return response_surface,response_air

    def get_sorted_estimations(self, all_estimations):
        sorted_estimations = sorted(all_estimations, key=lambda d: d["total_charge"])
        return sorted_estimations

    def get_shipping_estimation(self, db: Session, data,logger):
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
                surface_estimation, air_estimation = estimation_func(order_info=data)
                all_estimations.extend([surface_estimation, air_estimation])
            except Exception as e:
                logger.info(f"Error estimating shipping with {partner_name}: {str(e)}")


        sorted_estimations = self.get_sorted_estimations(all_estimations)
        return sorted_estimations
    
rate_calculation = CRUDRate(Partner)
