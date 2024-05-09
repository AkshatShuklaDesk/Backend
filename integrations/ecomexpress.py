from datetime import datetime
import json
from os import environ
import random
import string
from typing import Optional
import dotenv
import httpx
from fastapi.encoders import jsonable_encoder
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import xml.etree.ElementTree as ET
import constants
import schemas
from schemas.common import TrackDetail, TrackingResponse
from schemas.ecomexpress import shipment
# from schemas.xpress.shipment import (
#     User
# )

dotenv.load_dotenv()


class ecomExpress:
    BASE_URL = constants.ecomExpress
    def __init__(self):
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
                
            },
            timeout=httpx.Timeout(10.0),
        )

    # def auth(self, email,password):
    #     url = "https://ship.xpressbees.com/saas/authtoken"
    #     response = self._client.get(
    #         url,
    #         data = {"email":email , "password" : password},
    #     )
    #     response.raise_for_status()
    #     return response.json()
    
    # BASE_URL = "https://api.example.com/shipment"
    username="BEUTOPIANTECHNOSOFTPRIVATELIMITED433770"
    password="tmQs5qYtEL"
    @staticmethod
    def generate_boundary():
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))

    def create_shipment(self, shipment_data:schemas.ShipmentRequest):
        print(jsonable_encoder(shipment_data))
        url = "https://api.ecomexpress.in/apiv2/manifest_awb/"
        shipment_data=jsonable_encoder(shipment_data)
        data={
            "username":self.username,
            "password":self.password,
            "json_input":json.dumps([shipment_data]),
        }
        multipart_data=MultipartEncoder(fields=data)
        headers={'Content-Type': multipart_data.content_type}
        response = requests.post(url, data=multipart_data, headers=headers)
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

        url = "https://plapi.ecomexpress.in/track_me/api/mawbd/"
        
        data = {
            "username":self.username,
            "password":self.password,
            "awb": tracking_number,
            }
        
        multipart_data=MultipartEncoder(
                    fields=data
                )
        
        headers={'Content-Type': multipart_data.content_type}
        response = requests.post(url, data=multipart_data, headers=headers)
        print(type(response))
        print(response)
        print(response.content)
        response=response.content
        response = response.decode('utf-8')

        def xml_to_json(xml_string):
            root = ET.fromstring(xml_string)

            data = {}

            for obj in root.findall('.//object'):
                obj_data = {}
                obj_pk = obj.attrib['pk']
                obj_model = obj.attrib['model']

                for field in obj.findall('field'):
                    field_name = field.attrib['name']
                    field_value = field.text
                    obj_data[field_name] = field_value

                data[obj_pk] = {
                    'model': obj_model,
                    'fields': obj_data
                }

            json_data = json.dumps(data, indent=4)
            return json_data
        json_data=xml_to_json(response)
        def fetch_most_updated_info(json_data):
            data = json.loads(json_data)

            most_updated_info = {
                "status": None,
                "origin": None,
                "destination": None,
                "last_update_datetime_str": None,
                "orderid": None,
                "awb_number": None
            }
            most_updated_datetime = datetime.min

            for obj_id, obj_info in data.items():
                obj_fields = obj_info['fields']

                update_datetime_str = obj_fields.get('updated_on')
                if update_datetime_str:
                    update_datetime = datetime.strptime(update_datetime_str.strip(), '%d %b, %Y, %H:%M')

                    if update_datetime > most_updated_datetime:
                        most_updated_datetime = update_datetime
                        most_updated_info["status"] = obj_fields.get('status')
                        most_updated_info["origin"] = obj_fields.get('location_city')
                        most_updated_info["destination"] = obj_fields.get('city_name')
                        most_updated_info["last_update_datetime_str"] = update_datetime_str.strip()
                        most_updated_info["orderid"] = obj_fields.get('orderid')
                        most_updated_info["awb_number"] = obj_fields.get('awb_number')

            return most_updated_info



        most_updated_status = fetch_most_updated_info(json_data)
        return most_updated_status

        
    
    def fetch_waybill(self):
        url="https://api.ecomexpress.in/apiv2/fetch_awb/"
        data={
            "username":self.username,
            "password":self.password,
            "count":"1",
            "type":"cod",
        }
        multipart_data=MultipartEncoder(fields=data)
        headers={'Content-Type': multipart_data.content_type}
        response = requests.post(url, data=multipart_data, headers=headers)
        return response
    
    def rate_calculation(self,order):
        url="https://ratecard.ecomexpress.in/services/rateCalculatorAPI/"
        order=dict(order)
        shipment_data=jsonable_encoder(order)
        data={
            "username":self.username,
            "password":self.password,
            "json_input":json.dumps([shipment_data]),
        }
        multipart_data=MultipartEncoder(fields=data)
        headers={'Content-Type': multipart_data.content_type}
        response = requests.post(url, data=multipart_data, headers=headers)


        return response.json()
    
    def cancel_shipment(self,awb):
        url="https://api.ecomexpress.in/apiv2/cancel_awb/"
        data = {
            "username":self.username,
            "password":self.password,
            "awbs": awb,
            }
        
        multipart_data=MultipartEncoder(
                    fields=data
                )
        print(multipart_data)
        headers={'Content-Type': multipart_data.content_type}
        response = requests.post(url, data=multipart_data, headers=headers)

      

        return response.json()
    
    def convert_to_tracking_response(self,data: dict) -> TrackingResponse:
        details = TrackDetail(
            status=data['status'],
            origin=data['origin'],
            destination=data['destination'],
            timestamp= datetime.strptime(data["last_update_datetime_str"], '%d %b, %Y, %H:%M')
        )
        
        tracking_response = TrackingResponse(
            order_id=data['orderid'],
            waybill_no=data['awb_number'],
            partner_name="Ecomeexpress",
            details=[details]
        )
        
        return tracking_response
    

    def return_shipment(self, shipment_data:schemas.EcomexpressObjectsReturn):
        print(jsonable_encoder(shipment_data))
        url = "https://api.ecomexpress.in/apiv2/manifest_awb_rev_v2/"
        shipment_data=jsonable_encoder(shipment_data)
        shipment_data={"ECOMEXPRESS-OBJECTS":shipment_data}
        data={
            "username":self.username,
            "password":self.password,
            "json_input":json.dumps(shipment_data),
        }
        multipart_data=MultipartEncoder(fields=data)
        headers={'Content-Type': multipart_data.content_type}
        response = requests.post(url, data=multipart_data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
