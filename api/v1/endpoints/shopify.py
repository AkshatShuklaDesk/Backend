import binascii
from datetime import datetime
import os
import traceback
from typing import Literal

import httpx
import shopify
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from multipart.multipart import logging
from pydantic import BaseModel, HttpUrl

from shopify.utils import shop_url
from sqlmodel import Session
from api.deps import get_db
from api.v1.endpoints.orders import create_order

from core.logging_utils import setup_logger
from schemas.order import (
    AddressDetail,
    AddressInfo,
    OrderCreate,
    PaymentInfo,
    ProductInfo,
    UserInfo,
)
from crud import order
from temp import test_user
import dotenv

dotenv.load_dotenv()
api_version = "2024-01"

shopify.Session.setup(
    api_key=os.environ.get("SHOPIFY_KEY"), secret=os.environ.get("SHOPIFY_SECRET")
)

log_name = "shopify"
endpoint_device_logger_setup = setup_logger(log_name, level="INFO")
logger = logging.getLogger(log_name)
APP_URL = "https://9d29-43-252-197-60.ngrok-free.app"
router = APIRouter()

stores = {"quickstart-22efef6e.myshopify.com": "shpua_70286ce6232076030b57f0179b406207"}

def handle_fulfillment(order):
    destination = order.get("destination", {})
    order = create_order(
        order_in=OrderCreate(
            order_id=order.get("order_id"),
            buyer_info=UserInfo(
                contact_no=destination.get("phone"),
                first_name=destination.get("first_name"),
                email_address=destination.get("email"),
            ),
            address_info=AddressDetail(
                complete_address=destination.get("address1"),
                pincode=destination.get("zip"),
                city=destination.get("city"),
                state=destination.get("province"),
                country=destination.get("country"),
            ),
            billing_info=AddressInfo(
                contact_no=destination.get("phone"),
                first_name=destination.get("first_name"),
                email_address=destination.get("email"),
                complete_address=destination.get("address1"),
                pincode=destination.get("zip"),
                city=destination.get("city"),
                state=destination.get("province"),
                country=destination.get("country"),
            ),
            date=datetime.now(),
            channel="shopify",
        )
    )
    # location = shopify.Location().find_one(order.get("assigned_location_id"))
    # "https://{shop}.myshopify.com/admin/api/{api_version}/fulfillments.json"


def handle_cancellation(order):
    pass


@router.get("/redirect")
def redirect(url: HttpUrl):
    sanitized_url = shop_url.sanitize_shop_domain(url)
    if not sanitized_url:
        return HTTPException(status_code=422, detail="Shop must match")
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    redirect_uri = f"{APP_URL}/shopify/callback"
    scopes = [
        "write_fulfillments",
        "read_assigned_fulfillment_orders",
        "write_assigned_fulfillment_orders",
        "write_shipping",
        "read_orders",
    ]

    session = shopify.Session(sanitized_url, api_version)
    auth_url = session.create_permission_url(scopes, redirect_uri, state)
    return {"auth_url": auth_url}


@router.get("/callback")
def callback(
    code: str,
    state: str,
    hmac: str,
    host: str,
    shop: str,
    timestamp: int,
):
    try:
        params = locals()
        if not shopify.Session.validate_params(params):
            return HTTPException(status_code=403)
        session = shopify.Session(shop, api_version)
        access_token = session.request_token(params)
        stores[shop] = access_token
        # url = f"https://{shop}/admin/api/{api_version}/fulfillment_services.json"
        # res = httpx.post(
        #     url,
        #     json={
        #         "fulfillment_service": {
        #             "name": "Cargo Cloud fulfillment service",
        #             "callback_url": f"{APP_URL}/shopify",
        #             "inventory_management": True,
        #             "permits_sku_sharing": True,
        #             "tracking_support": False,
        #             "requires_shipping_method": True,
        #             "format": "json",
        #             "fulfillment_orders_opt_in": True,
        #         }
        #     },
        #     headers={"X-Shopify-Access-Token": access_token},
        # )
        # print(res.json())
        url = f"https://{shop}/admin/api/{api_version}/webhooks.json"
        res = httpx.post(
            url,
            json={
                "webhook": {
                    "topic": "orders/create",
                    "address": f"{APP_URL}/shopify/webhook",
                    "format": "json",
                }
            },
            headers={"X-Shopify-Access-Token": access_token},
        )
        print(res.json())
        return RedirectResponse(url="http://43.252.197.60:7200")
    except Exception:
        traceback.print_exc()
        return HTTPException(status_code=403)


class Notification(BaseModel):
    kind: Literal["fulfillment_request", "cancellation_request"]


@router.post("/fulfillment_order_notification")
def order_notification(body: Notification):
    shop = "quickstart-22efef6e.myshopify.com"
    access_token = stores[shop]
    url = f"https://{shop}/admin/api/2024-01/assigned_fulfillment_orders.json"
    res = httpx.get(
        url,
        params={"assignment_status": body.kind + "ed"},
        headers={"X-Shopify-Access-Token": access_token},
    )
    data = res.json()
    print("full", data)
    for order_data in data["fulfillment_orders"]:
        if body.kind == "fulfillment_request":
            handle_fulfillment(order_data)
        else:
            handle_cancellation(order_data)


@router.post("/webhook")
def webhook(body: dict, db: Session = Depends(get_db)):
    try:
        shop = "quickstart-22efef6e.myshopify.com"
        print(body)
        url = f"https://{shop}/admin/api/2024-01/locations/{body.get('location_id', '')}.json"
        access_token = stores[shop]
        res = httpx.get(
            url,
            headers={"X-Shopify-Access-Token": access_token},
        )
        location = res.json()
        print(location)
        billing = body.get("biiling_address", {})
        customer = body.get("customer", {})
        shipping = body.get("shipping_address", {})
        payment = body.get("payment_terms", {}) or {}
        order_id = order.generate_order_id(db=db, user_id=test_user.id)
        products = []
        for product in body.get("line_items", []):
            products.append(
                ProductInfo(
                    name=product.get("name"),
                    unit_price=product.get("price"),
                    quantity=product.get("quantity"),
                    sku=product.get("sku"),
                    hsn_code=product.get("sku"),
                )
            )
        generated = create_order(
            db=db,
            order_in=OrderCreate(
                order_id=str(order_id),
                buyer_info=UserInfo(
                    contact_no=customer.get("phone", "")[1:],
                    first_name=customer.get("first_name"),
                    email_address=customer.get("email"),
                ),
                address_info=AddressDetail(
                    complete_address=shipping.get("address1"),
                    pincode=shipping.get("zip"),
                    city=shipping.get("city"),
                    state=shipping.get("province"),
                    country=shipping.get("country"),
                ),
                billing_info=AddressInfo(
                    contact_no=billing.get("phone", "")[1:],
                    first_name=billing.get("first_name"),
                    email_address=customer.get("email"),
                    complete_address=billing.get("address1"),
                    pincode=billing.get("zip"),
                    city=billing.get("city"),
                    state=billing.get("province"),
                    country=billing.get("country"),
                ),
                date=datetime.now(),
                channel="shopify",
                total_amount=body.get("total_price"),
                pickup_address=AddressInfo(
                    id=152
                ),
                product_info=products,
                order_type="domestic",
                height=1,
                width=1,
                applicable_weight=body.get("total_weight", 0) / 1000,
                payment_details=PaymentInfo(
                    type="prepaid"
                    if payment.get("payment_terms_type", "NET") == "NET"
                    else "cod"
                ),
            ),
        )
        print(generated)
    except Exception:
        traceback.print_exc()
