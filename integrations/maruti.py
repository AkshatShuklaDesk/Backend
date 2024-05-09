from datetime import datetime
import json
from os import environ
from typing import Optional

import dotenv
import httpx
from fastapi.encoders import jsonable_encoder
import requests

import constants
import schemas
from schemas.common import TrackDetail, TrackingResponse
from schemas.xpressbees import waybill
# from schemas.xpress.shipment import (
#     User
# )

dotenv.load_dotenv()


class maruti:
    BASE_URL = constants.MARUTI_URL
    # api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MTE2MTIwNTAsImp0aSI6ImVxRHlwc0hqZURZdSsyRGExQnVKTFF0Vit5enhBbTBQUnBRR01HdGM5K2M9IiwibmJmIjoxNzExNjEyMDUwLCJleHAiOjE3MTE2MjI4NTAsImRhdGEiOnsidXNlcl9pZCI6IjcwNzM1IiwicGFyZW50X2lkIjoiMCIsImlzX2ZyYW5jaGlzZSI6Im5vIiwiZW1haWwiOiJkZW1vQHhwcmVzc2JlZXMuY29tIn19.bqQttVnMMWQYLdONmpjKNaRsP7gJ6sh_u_1R3QN_rQfuRfMHKPjN2s0NMJJVGbdW4eZ-CxTsUdWHCsuAo6oe_Q"
    def __init__(self):
        
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(10.0),

        )
        auth_res=self.auth(email="munjal.varma@spidit.in",password="Delcaper@123",vendorType="SELLER")
        self.api_key=auth_res["data"]["accessToken"]
       

    def auth(self, email,password,vendorType):
        url = "https://qaapis.delcaper.com/auth/login"
        headers = {
            "Content-Type": "application/json",
        }
        response = self._client.post(
            url=url,
            json= {"email":email , "password" : password,"vendorType":vendorType},
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    # BASE_URL = "https://api.example.com/shipment"

    def push_order(self, shipment_data:schemas.ShipmentRequest):
            print(jsonable_encoder(shipment_data))
            url = "https://qaapis.delcaper.com/fulfillment/public/seller/order/ecomm/push-order"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = self._client.post(url, json=jsonable_encoder(shipment_data), headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.is_success== False:
                return response.json()
            else:
                return {"error": response.text,"status":response.status_code}

    def track_shipment(
        self,  awbNumber: Optional[int] = None
    ) -> TrackingResponse:
       
        if awbNumber:
            tracking_number = awbNumber
        else:
            raise ValueError("Must pass Waybill or Awb number")

        url = f"https://qaapis.delcaper.com/fulfillment/public/seller/order/order-tracking/{awbNumber}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        
        data = response.json()
        print(data)
        response={
            "status":data["data"]["orderStatus"],
            "origin":"",
            "destination":"",
            "timestamp":data["data"]["orderCreatedAt"]

        }
        return TrackingResponse(
            partner_name="maruti",
            details=[response],
        )
    

    def cancel_shipment(self,order_id):
        url="https://qaapis.delcaper.com/fulfillment/public/seller/order/cancel-order"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "orderId": order_id,
            "cancelReason":"Cancel Test"
            }
        response = requests.put(url, json=data, headers=headers)
        


        return response.content
    

    def rate_calculation(self,order):
        url="https://qaapis.delcaper.com/fulfillment/rate-card/calculate-rate/ecomm"
        order=dict(order)
        shipment_data=jsonable_encoder(order)
        
        headers={"Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
                 }
        response = requests.post(url, json=shipment_data, headers=headers)


        return response.json()
    
    
    def create_shipment(self, response:dict):
        url = "https://qaapis.delcaper.com/fulfillment/public/seller/order/create-manifest"

        data={
            "awbNumber": [response["data"]["awbNumber"]]
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = self._client.post(url, json=data, headers=headers)

        if response.status_code == 201:
            return response.json()
        else:
            return {"error": response.text}
