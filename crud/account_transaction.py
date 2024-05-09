import datetime
from copy import deepcopy
from typing import Dict, cast
from sqlalchemy import Date
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, aliased
from decimal import Decimal

from city_mapping import cities
from crud.base import CRUDBase
from models.account_transaction import AccountTransaction
from schemas.account_transaction import AccountTransactionCreate, AccountTransactionBase
class CRUDAccountTransaction(CRUDBase[AccountTransaction, AccountTransactionCreate, AccountTransactionBase]):
    def get_account_transaction_report(self, db: Session, filter_dict: Dict,offset:int,limit:int):
        date_from = filter_dict['date_from'].split('T')[0]
        date_to = filter_dict['date_to'].split('T')[0]
        date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d')
        created_from = filter_dict['user_id']
        """
        Opening Balance Calculation.
        For Calculating opening balance we will do follwing things
        1) Calculate past transaction opening balance. 
        That will be calculated from Financial year starting to report report_from_date.
        2) Check if we have already saved opening balance in the db or not.
        3) Merge result from 1 and 2
        4) Append calculated opening balance into final list
        """
        """
        1
        """
        """
        2
        """
        opening_balance_dict = 0
        final_list = []
        # if opening_balance_dict:
        #     opening_balance_dict['remarks'] = 'Opening Balance'
        #     opening_bal = opening_balance_dict['balance']
        #     opening_bal_type = opening_balance_dict['balance_type']
        #     if not opening_bal:
        #         opening_bal = 0
        #         opening_bal_type = 'Dr'
        # else:
        opening_bal = 0
        opening_bal_type = 'Dr'
        """
        3
        """
        balance_type = "Dr"
        balance = 0
        if str(balance_type).lower() == str(opening_bal_type).lower():
            balance += opening_bal
        elif balance >= opening_bal:
            balance -= opening_bal
        else:
            balance = opening_bal - balance
            balance_type = opening_bal_type

        """
        4
        """
        final_list.append({
            "remarks": "OPENING BALANCE",
            "balance": balance,
            "balance_type": balance_type,
            "date": '-'.join(str(date_from.date()).split('-')[::-1])
        })
        results = db.query(self.model).select_from(self.model).filter(self.model.date >= date_from, self.model.date <= date_to, self.model.party_id == created_from).order_by(self.model.id.desc()).offset(offset).limit(limit).all()
        """
        Sortting of result as per logic
        1) Get debit entries of all first
        2) Then Credit entried aftterwards
        3) Voucher type wise sorting
        4) Voucher id wise sorting
        5) Sequence wise sorting
        """
        results_sorted = []
        previous_date = None
        temp_list = []
        if len(results) > 1:
            for num, res in enumerate(results):
                res = jsonable_encoder(res)
                # print (res[0]["debit"], res[0]["credit"],res)
                res["new_date"] = '-'.join(res["date"].split('T')[0].split('-')[::-1])
                # print ("new date", res[0]["new_date"])
                if (res["new_date"] != previous_date and previous_date is not None) or (
                        num == len(results) - 1 and res["new_date"] == previous_date):
                    if num == len(results) - 1 and res["new_date"] == previous_date:
                        temp_list.append(res)
                    """
                    First get all debit entries
                    Then get all credit entries
                    """
                    debit_entries = []
                    credit_entries = []
                    for temp in temp_list:
                        if temp["debit"]:
                            debit_entries.append(temp)
                        else:
                            credit_entries.append(temp)
                    debit_entries = sorted(debit_entries, key=lambda i: (i['voucher_type'], i['voucher_id']))
                    credit_entries = sorted(credit_entries, key=lambda i: (i['voucher_type'], i['voucher_id']))
                    results_sorted.extend(debit_entries)
                    results_sorted.extend(credit_entries)
                    if num == len(results) - 1 and res["new_date"] != previous_date:
                        results_sorted.append(res)
                    temp_list = []
                    pass
                temp_list.append(res)
                previous_date = ["new_date"]

        for res in results_sorted:
            res = jsonable_encoder(res)
            if res['voucher_type'] not in ['cr', 'cp', 'br', 'bp', 'jv']:
                is_freight_report = False
            if res['debit'] is not None:
                res['debit'] = Decimal(res['debit'])
            if res['credit'] is not None:
                res['credit'] = Decimal(res['credit'])
            if res['balance'] is not None:
                res['balance'] = Decimal(res['balance'])
            if res['credit']:
                if balance_type.lower() == 'cr':
                    balance += res['credit']
                else:
                    balance -= res['credit']
            else:
                if balance_type.lower() == 'dr':
                    balance += res['debit']
                else:
                    balance -= res['debit']
            if balance <= 0 and balance_type.lower() == "dr":
                balance_type = 'Cr'
                balance = abs(balance)
            elif balance <= 0 and balance_type.lower() == "cr":
                balance_type = 'Dr'
                balance = abs(balance)
            temp_dict = res
            temp_dict['balance'] = balance
            # temp_dict['balance_type'] = balance_type
            temp_dict['remarks'] = res['remarks'].upper() if res['remarks'] else ''
            temp_dict['orignal_date'] = temp_dict['date']
            temp_dict["date"] = '-'.join(temp_dict["date"].split('T')[0].split('-')[::-1])
            temp_dict['voucher_type'] = res['voucher_type'].upper()
            # temp_dict['source_party_name'] = res[2]['name']
            # temp_dict['party_name'] = res[3]['name']
            # temp_dict['created_from'] = res[1]['name']
            temp_dict['created_date'] = '-'.join(res['created_date'].split('T')[0].split('-')[::-1])
            final_list.append(deepcopy(temp_dict))
        is_freight_report = False
        if is_freight_report:
            opening_entry = final_list
            new_list = []
            new_list.append(opening_entry)
            final_list = sorted(final_list[1:], key=lambda i: (i['orignal_date'], i['voucher_type']))
            balance = opening_entry['balance']
            balance_type = opening_entry['balance_type']
            for item in final_list:
                if item['credit']:
                    if balance_type.lower() == 'cr':
                        balance += item['credit']
                    else:
                        balance -= item['credit']
                else:
                    if balance_type.lower() == 'dr':
                        balance += item['debit']
                    else:
                        balance -= item['debit']
                if balance <= 0 and balance_type.lower() == "dr":
                    balance_type = 'Cr'
                    balance = abs(balance)
                elif balance <= 0 and balance_type.lower() == "cr":
                    balance_type = 'Dr'
                    balance = abs(balance)
                item['balance'] = balance
                item['balance_type'] = balance_type
            new_list.extend(final_list)
            # final_list = list(opening_entry) + sorted(final_list[1:], key = lambda i: i['voucher_type'])
            return new_list
        else:
            return final_list

    def create_account_transaction_entry(self, db: Session, account_obj):
        created_from = account_obj["created_by"]
        debit_party = 1
        credit_party = 2
        # next_unique_id = last_id_info.last_account_transaction_id + 1
        fyear = "23-24"
        companyid = 1
        voucher_type = "Order-" + str(account_obj["user_id"])
        voucher_id = account_obj["order_id"]
        # amount = to_pay_amt
        date = str(account_obj['created_date']).split('T')[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        created_by = account_obj['created_by']
        created_date = datetime.datetime.now()
        modified_date = datetime.datetime.now()
        unique_id = 1
        amount = account_obj["amount"]
        remarks = "Order account transaction"

        if amount == 0:
            return None

        acc_obj1 = {
            "party_id": debit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "credit": Decimal(0),
            "debit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": credit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }
        acc_obj2 = {
            "party_id": credit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "debit": Decimal(0),
            "credit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": debit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }
        db_obj1 = self.model(**acc_obj1)
        db_obj2 = self.model(**acc_obj2)
        db.add(db_obj1)
        db.add(db_obj2)
        db.flush()
        db.refresh(db_obj1)
        db.refresh(db_obj2)
        return db_obj1.id
    def order_transaction(self, db: Session, order_obj, partner_info):
        partner_info = jsonable_encoder(partner_info)
        created_from = order_obj["users_id"]
        debit_party = order_obj["users_id"]
        credit_party = 1000
        # next_unique_id = last_id_info.last_account_transaction_id + 1
        fyear = "23-24"
        companyid = 1
        voucher_type = str(order_obj["waybill_no"])
        voucher_id = order_obj["id"]
        date = str(order_obj['created_date']).split('T')[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        created_by = order_obj['users_id']
        created_date = datetime.datetime.now()
        modified_date = datetime.datetime.now()
        unique_id = 1
        amount = partner_info["amount"]
        remarks = f"Order:- {voucher_id}, {voucher_type}"

        if amount == 0:
            return None

        acc_obj1 = {
            "party_id": debit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "credit": Decimal(0),
            "debit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": credit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }
        acc_obj2 = {
            "party_id": credit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "debit": Decimal(0),
            "credit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": debit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }
        db_obj1 = self.model(**acc_obj1)
        db_obj2 = self.model(**acc_obj2)
        db.add(db_obj1)
        db.add(db_obj2)
        db.flush()
        db.refresh(db_obj1)
        db.refresh(db_obj2)
        return db_obj1
    def recharge_transaction(self, db: Session, order_obj):
        order_obj = jsonable_encoder(order_obj)
        created_from = order_obj["user_id"]
        debit_party = 1000
        credit_party = order_obj["user_id"]
        # next_unique_id = last_id_info.last_account_transaction_id + 1
        fyear = "23-24"
        companyid = 1
        voucher_type = "RCH-" + str(order_obj["id"])
        voucher_id = order_obj["id"]
        date = str(order_obj['created_date']).split('T')[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        created_by = order_obj['user_id']
        created_date = datetime.datetime.now()
        modified_date = datetime.datetime.now()
        unique_id = 1
        amount = order_obj["amount"]
        remarks = f"Recharge of Amount:- {amount}"

        if amount == 0:
            return None

        acc_obj1 = {
            "party_id": debit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "credit": Decimal(0),
            "debit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": credit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }
        acc_obj2 = {
            "party_id": credit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "debit": Decimal(0),
            "credit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": debit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }

        db_obj1 = self.model(**acc_obj1)
        db_obj2 = self.model(**acc_obj2)
        db.add(db_obj1)
        db.add(db_obj2)
        db.flush()
        db.refresh(db_obj1)
        db.refresh(db_obj2)
        return db_obj1

    def indent_approval(self, db: Session, indent_obj):
        indent_obj = jsonable_encoder(indent_obj)
        created_from = indent_obj["created_by"]
        debit_party = indent_obj['created_by']
        credit_party = 1000
        # next_unique_id = last_id_info.last_account_transaction_id + 1
        fyear = "23-24"
        companyid = 1
        voucher_type = "INDENT-" + str(indent_obj["id"])
        voucher_id = indent_obj["id"]
        date = str(indent_obj['created_date']).split('T')[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        created_by = indent_obj['created_by']
        created_date = datetime.datetime.now()
        modified_date = datetime.datetime.now()
        unique_id = 1
        amount = indent_obj["actual_price"] if indent_obj["actual_price"] else 0
        station_from = cities[str(indent_obj['source_id'])]
        station_to = cities[str(indent_obj['destination_id'])]
        remarks = f"Indent created from {station_from} to {station_to}"

        if amount == 0:
            return None

        acc_obj1 = {
            "party_id": debit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "credit": Decimal(0),
            "debit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": credit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }
        acc_obj2 = {
            "party_id": credit_party,
            "voucher_type": voucher_type,
            "voucher_id": voucher_id,
            "debit": Decimal(0),
            "credit": amount,
            "cheque_no": None,
            "remarks": remarks,
            "balance": 0,
            "balance_type": "Dr",
            "date": date,
            "created_from": created_from,
            "created_by": created_by,
            "created_date": created_date,
            "modified_date": modified_date,
            "unique_id": unique_id,
            "other_party_id": debit_party,
            "account_id": None,
            "bank_name": None,
            "clearance_status": None,
            "clearance_date": None,
            "fyear": str(fyear),
            "companyid": companyid,
        }

        db_obj1 = self.model(**acc_obj1)
        db_obj2 = self.model(**acc_obj2)
        db.add(db_obj1)
        db.add(db_obj2)
        db.flush()
        db.refresh(db_obj1)
        db.refresh(db_obj2)
        return db_obj1

account_transaction = CRUDAccountTransaction(AccountTransaction)
