from datetime import datetime
from os import environ
from typing import Optional

import dotenv
import httpx
from schemas.common import TrackDetail, TrackingResponse

from schemas.dtdc.shipment import Consignment

dotenv.load_dotenv()


class DTDCClient:
    STATUS_MAP = {
        "booked": "Manifested",
        "in transit": "In Transit",
        "reached at destination": "Reached Destination",
        "out for delivery": "Out for Delivery",
        "delivered": "Delivered",
        "pickup awaited": "Pickup Awaited",
        "softdata upload": "Softdata Upload"
    }

    def __init__(self) -> None:
        api_key = environ.get("DTDC_API_KEY")
        if not api_key:
            raise Exception("Missing DTDC_API_KEY environment variable")

        self._client = httpx.Client(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "api-key": api_key,
                "X-Access-Token": api_key,
            },
            timeout=httpx.Timeout(10.0),
        )

    def check_pincode(self, origin: str, dest: str):
        url = "http://smarttrack.ctbsplus.dtdc.com/ratecalapi/PincodeApiCall"
        response = self._client.post(
            url,
            json={
                "orgPincode": origin,
                "desPincode": dest,
            },
        )
        response.raise_for_status()
        return response.json()

    def create_warehouse(self):
        raise NotImplementedError()

    def update_warehouse(self):
        raise NotImplementedError()

    def fetch_waybill(self) -> list[int]:
        raise NotImplementedError()

    def calculate_shipping(self):
        raise NotImplementedError()

    def create_shipment(self, consignments: list[Consignment]):
        url = "https://dtdcapi.shipsy.io/api/customer/integration/consignment/softdata"
        data = []
        # DTDC only supports 20 consignments per call. So we are calling API in chunks of 20
        for i in range(0, len(consignments), 20):
            payload = map(
                lambda x: x.model_dump(exclude_none=True), consignments[i : i + 20]
            )
            response = self._client.post(
                url,
                json={"consignments": list(payload)},
            )
            response.raise_for_status()
            data.extend(response.json()["data"])
        return data

    def update_shipment(self):
        raise NotImplementedError()

    def cancel_shipment(self, waybills: list[str], customer_code: str):
        url = "http://dtdcapi.shipsy.io/"
        response = self._client.post(
            url + "api/customer/integration/consignment/cancel",
            json={"AWBNo": waybills, "customerCode": customer_code},
        )
        response.raise_for_status()
        return response.json()

    def transform_tracking(self, step):

        parsed_dt = datetime.strptime(
            step["strActionDate"] + step["strActionTime"], "%d%m%Y%H%M"
        )
        parsed_status = self.STATUS_MAP.get(step["strAction"].lower(), "UNKNOWN")
        data = TrackDetail(
            status=parsed_status,
            origin=step.get("strOrigin", ""),
            destination=step.get("strDestination", ""),
            timestamp=parsed_dt,
        )
        return data

    def track_shipment(
        self, reference_no: Optional[str] = None, consignment_no: Optional[str] = None
    ) -> TrackingResponse:
        if reference_no:
            track_type = "reference"
            tracking_number = reference_no
        elif consignment_no:
            track_type = "cnno"
            tracking_number = consignment_no
        else:
            raise ValueError("Must pass either reference_no or consignment_no")

        access_token = "AL316_trk_json:a20469e69ffd986b30428bb578f6c9b5"
        url = "https://blktracksvc.dtdc.com/dtdc-api/rest/JSONCnTrk/getTrackDetails"
        response = self._client.post(
            url,
            headers={"X-Access-Token": access_token},
            json={
                "TrkType": track_type,
                "strcnno": tracking_number,
                "addtnlDtl": "Y",
            },
        )
        response.raise_for_status()
        data = response.json()
        data['trackDetails'].reverse()
        return TrackingResponse(
            partner_name="DTDC",
            details=list(map(self.transform_tracking, data["trackDetails"])),
        )

    def generate_shipping_label(self, reference_number: str):
        url = "https://dtdcapi.shipsy.io/api/customer/integration/consignment/shippinglabel/link"
        response = self._client.post(url, data={"reference_number": reference_number})
        response.raise_for_status()
        return response.json()

    def raise_pickup_request(self):
        raise NotImplementedError()
