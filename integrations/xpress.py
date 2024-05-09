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


class xpressClient:
    BASE_URL = constants.XPRESS_URL
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
        auth_res=self.auth(email="demo@xpressbees.com",password="demo@123")
        self.api_key=auth_res["data"]
       

    def auth(self, email,password):
        url = "https://ship.xpressbees.com/saas/authtoken"
        headers = {
            "Content-Type": "application/json"
        }
        response = self._client.post(
            url=url,
            json= {"email":email , "password" : password},
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    # BASE_URL = "https://api.example.com/shipment"

    def create_shipment(self, shipment_data:schemas.ShipmentRequest):
        print(jsonable_encoder(shipment_data))
        url = "https://ship.xpressbees.com/saas/waybill"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = self._client.post(url, json=jsonable_encoder(shipment_data), headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
        
    def track_shipment(
        self,  awb_no: Optional[str] = None
    ) -> TrackingResponse:
       
        if awb_no:
            tracking_number = awb_no
        else:
            raise ValueError("Must pass Waybill or Awb number")

        url = "https://ship.xpressbees.com/saas/waybilldetails"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "awb_number": tracking_number,
            }
        response = requests.get(url, headers=headers, json=data)
        
        data = response.json()
        print(data)
        return TrackingResponse(
            partner_name="Xpress",
            detailsxpress=data,
        )
    

    def cancel_shipment(self,awb):
        url="https://ship.xpressbees.com/saas/cancel"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "awb_number": awb,
            }
        response = requests.post(url, json=data, headers=headers)
        


        return response.content
    
    def calculate_shipping(self, order_info):
        url="https://shipment.xpressbees.com/api/courier/serviceability"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        order_info=jsonable_encoder(order_info)
        response = requests.post(url, json=order_info, headers=headers)
        response=response.content
        response_content_str = response.decode('utf-8')
        response_data = json.loads(response_content_str)
        # response.raise_for_status()
        return response_data
    

    def return_shipment(self, shipment_data:schemas.ShipmentRequest):
        print(jsonable_encoder(shipment_data))
        url = "https://ship.xpressbees.com/saas/waybill"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = self._client.post(url, json=jsonable_encoder(shipment_data), headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}

