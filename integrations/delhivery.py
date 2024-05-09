from datetime import datetime
import json
from os import environ
from typing import Optional

import dotenv
import httpx

import constants
from schemas.common import TrackDetail, TrackingResponse
from schemas.delhivery.shipment import (
    CreateShipment,
    GetShippingCost,
    UpdateShipment,
    PickupDetail,
)
from schemas.delhivery.warehouse import CreateWarehouse, UpdateWarehouse

dotenv.load_dotenv()


class DelhiveryClient:
    BASE_URL = constants.DELHIVERY_URL
    STATUS_MAP = {
        "manifested": "Manifested",
        "in transit": "In Transit",
        "reached at destination": "Reached Destination",
        "out for delivery": "Out for Delivery",
        "delivered": "Delivered",
        "not picked": "Not Picked",
        "pending": "Shipment Received at Facility",
        "dispatched": "Call placed to consignee",
        "rto": "RTO"
    }

    def __init__(self) -> None:
        api_key = environ.get("DELHIVERY_API_KEY")
        if not api_key:
            raise Exception("Missing DELHIVERY_API_KEY environment variable")

        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}",
            },
            timeout=httpx.Timeout(10.0),
        )

    def check_pincode(self, pincode: str):
        response = self._client.get(
            "c/api/pin-codes/json/", params={"filter_codes": pincode}
        )
        data = response.json()
        return data.get("delivery_codes")

    def create_warehouse(self, warehouse: CreateWarehouse):
        response = self._client.post(
            "api/backend/clientwarehouse/create/",
            json=warehouse.model_dump(by_alias=True),
        )
        response.raise_for_status()
        return response.json()

    def update_warehouse(self, name: str, data: UpdateWarehouse):
        response = self._client.post(
            "api/backend/clientwarehouse/edit/",
            json={"name": name, **data.model_dump(exclude_unset=True, by_alias=True)},
        )
        response.raise_for_status()
        return response.json()

    def fetch_waybill(self, count: int) -> list[int]:
        response = self._client.get("waybill/api/bulk/json/", params={"count": count})
        response.raise_for_status()
        return response.json().split(",")

    def calculate_shipping(self, params: GetShippingCost):
        response = self._client.get(
            "api/kinko/v1/invoice/charges/.json",
            params=params.model_dump(exclude_unset=True, by_alias=True),
        )
        response.raise_for_status()
        return response.json()

    def create_shipment(self, warehouse_name: str, shipments: list[CreateShipment]):
        payload = {
            "pickup_location": {"name": warehouse_name},
            "shipments": [shipment.model_dump(by_alias=True) for shipment in shipments],
        }
        response = self._client.post(
            "api/cmu/create.json",
            content=f"format=json&data={json.dumps(payload)}",
        )
        response.raise_for_status()
        return response.json()

    def update_shipment(self, waybill: str, data: UpdateShipment):
        response = self._client.post(
            "api/p/edit",
            json={
                "waybill": waybill,
                **data.model_dump(exclude_unset=True, by_alias=True),
            },
        )
        response.raise_for_status()
        return response.json()

    def cancel_shipment(self, waybill: str):
        response = self._client.post(
            "api/p/edit", json={"waybill": waybill, "cancellation": True}
        )
        response.raise_for_status()
        return response.json()

    def transform_tracking(self, detail):
        detail = detail["ScanDetail"]
        parsed_dt = datetime.fromisoformat(detail["StatusDateTime"])
        parsed_status = self.STATUS_MAP.get(detail["Scan"].lower(), detail["Instructions"] if detail["Scan"].lower() == "pending" else "UNKNOWN")
        return TrackDetail(
            status=parsed_status, origin="", destination="", timestamp=parsed_dt
        )

    def track_shipment(
        self,
        *,
        waybills: Optional[list[str]] = None,
        order_ids: Optional[list[str]] = None,
    ):
        response = self._client.get(
            "api/v1/packages/json/",
            params={
                "waybill": ",".join(waybills) if waybills else "",
                "ref_ids": ",".join(order_ids) if order_ids else "",
            },
        )
        response.raise_for_status()
        data = response.json()
        data = data["ShipmentData"][0]["Shipment"]
        return TrackingResponse(
            partner_name="Delhivery",
            details=list(map(self.transform_tracking, data["Scans"])),
            ReverseInTransit=data["ReverseInTransit"]
        )

    def generate_shipping_label(self, waybill: str, *, pdf=False):
        raise NotImplementedError()

    def raise_pickup_request(self, pickup_details: PickupDetail):
        response = self._client.post(
            "fm/request/new/", content=pickup_details.model_dump_json()
        )
        response.raise_for_status()
        return response.json()
