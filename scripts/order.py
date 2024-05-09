import csv
import codecs
from typing import Any
from fastapi import UploadFile
from copy import deepcopy

csv_cols = [
    "order_id",
    "date",
    "channel",
    "payment_type",
    "customer_first_name",
    "customer_last_name",
    "customer_email_address",
    "customer_contact_no",
    "customer_alternate_contact_no",
    "shipping_address_line1",
    "shipping_address_line2",
    "shipping_address_country",
    "shipping_address_state",
    "shipping_address_city",
    "shipping_address_pincode",
    "billing_address_line1",
    "billing_address_line2",
    "billing_address_country",
    "billing_address_state",
    "billing_address_city",
    "billing_address_pincode",
    "product_sku",
    "product_name",
    "product_quantity",
    "product_tax_rate",
    "product_unit_price",
    "product_discount",
    "payment_shipping_charges",
    "total_amount",
    "payment_gift_wrap",
    "payment_discount",
    "length",
    "width",
    "height",
    "applicable_weight",
    "send_notification",
    "comment",
    "product_hsn_code",
    "location_id",
    "reseller_name",
    "company_name",
    "latitude",
    "longitude",
    "verified_order",
    "is_documents",
    "order_type",
    "tag",
]


def convert_csv_data_to_json(csv_data):
    file_orders_json_list = []
    for row in csv_data:
        order_dict = {}
        for k, v in row.items():
            order_dict[k] = v
        file_orders_json_list.append(deepcopy(order_dict))
    return file_orders_json_list


def format_order_info(order_info):
    new_info: dict[str, Any] = {"other_charges": 0, "total_amount": 0 , "volumatric_weight":1}
    address_info = {}
    billing_info = {}
    company_info = {}
    buyer_info = {}
    payment_details = {}
    for k, v in order_info.items():
        if k.startswith("product"):
            continue
        elif k.startswith("shipping"):
            address_info[k.replace("shipping_address_", "")] = v
        elif "billing" in k:
            billing_info[k.replace("billing_address_", "")] = v
        elif "company" in k:
            company_info[k.replace("company_", "")] = v
        elif "customer" in k:
            buyer_info[k.replace("customer_", "")] = v
        elif k.startswith("payment"):
            payment_details[k.replace("payment_", "")] = v
            value = payment_details[k.replace("payment_", "")] or "0"
            if k == "payment_type":
                payment_details[k.replace("payment_", "")] = v.lower()
                continue
            if k == "payment_discount":
                new_info["other_charges"] -= int(value)
            else:
                new_info["other_charges"] += int(value)
        elif k.startswith("length"):
            new_info["length"] = v
            new_info["volumatric_weight"] *= float(v)
        elif k.startswith("width"):
            new_info["width"] = v
            new_info["volumatric_weight"] *= float(v)
        elif k.startswith("height"):
            new_info["height"] = v
            new_info["volumatric_weight"] *= round(float(float(v)/5000),6)

        else:
            new_info[k] = v
    return {
        **new_info,
        "address_info": address_info,
        "billing_info": {
            **billing_info,
            **buyer_info,
        },
        "pickup_address": {
            "id": order_info["location_id"]
        },
        "company_info": company_info,
        "buyer_info": buyer_info,
        "payment_details": payment_details

    }


def get_formatted_product_info(order_info):
    new_info = {}
    for k, v in order_info.items():
        if "product" in k:
            new_info[k.replace("product_", "")] = v
    return new_info


def update_name_to_id(order_info):
    return order_info


def create_order_info_from_file(file: UploadFile):
    reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"), fieldnames=csv_cols)
    reader = list(reader)
    reader.pop(0)
    for row in reader:
        # Iterate through each field in the row
        for field in row:
            # Check if the field is empty (i.e., an empty string)
            if row[field] == '':
                # Replace empty string with None
                row[field] = None
    order_set = set()
    order_id_value_dict = {}
    for order_info in reader:
        if order_info["order_id"] not in order_set:
            order_id_value_dict[order_info["order_id"]] = format_order_info(order_info)
            order_id_value_dict[order_info["order_id"]]["product_info"] = []
        order_id_value_dict[order_info["order_id"]]["product_info"].append(
            get_formatted_product_info(order_info)
        )
        if "sub_total" not in order_id_value_dict[order_info["order_id"]]:
            order_id_value_dict[order_info["order_id"]]["sub_total"] = 0
        order_id_value_dict[order_info["order_id"]]["sub_total"] += int(
            order_id_value_dict[order_info["order_id"]]["product_info"][-1][
                "unit_price"
            ]
        ) * int(
            order_id_value_dict[order_info["order_id"]]["product_info"][-1]["quantity"]
        )
        order_id_value_dict[order_info["order_id"]]["sub_total"] -= int(
            order_id_value_dict[order_info["order_id"]]["product_info"][-1]["discount"]
            or "0"
        ) * int(
            order_id_value_dict[order_info["order_id"]]["product_info"][-1]["quantity"]
        )
        order_set.add(order_info["order_id"])

    for order_id in order_id_value_dict:
        order_id_value_dict[order_id]["total_amount"] = (
            int(order_id_value_dict[order_id]["total_amount"] or "0")
            + order_id_value_dict[order_id]["sub_total"]
            + order_id_value_dict[order_id]["other_charges"]
        )
        order_id_value_dict[order_id] = update_name_to_id(order_id_value_dict[order_id])
    return list(order_id_value_dict.values())
