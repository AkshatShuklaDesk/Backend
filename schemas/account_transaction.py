from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal


# Shared properties
class AccountTransactionBase(BaseModel):
    pass


# Properties to receive on item creation
class AccountTransactionDetails(AccountTransactionBase):
    id: Optional[int] = None
    party_id: int
    account_id: Optional[int] = None
    voucher_type: Optional[str] = None
    voucher_id: Optional[int] = None
    credit: Optional[Decimal] = None
    debit: Optional[Decimal] = None
    cheque_no: Optional[str] = None
    other_party_id: Optional[int] = None
    unique_id: Optional[int] = None
    remarks: Optional[str] = None
    balance: Optional[Decimal] = None
    clearance_status: Optional[int] = None
    clearance_date: Optional[datetime] = None
    balance_type: Optional[int] = None
    account_id: Optional[int] = None
    date: Optional[datetime] = None
    created_date: Optional[datetime] = None
    created_from: Optional[int] = None
    created_by: Optional[int] = None
    bank_name: Optional[str] = None
    fyear: Optional[str] = None
    companyid: Optional[int] = None


class AccountTransactionCreate(AccountTransactionBase):
    account_transaction_info: List[AccountTransactionDetails] = None


class AccountTransactionUpdate(AccountTransactionBase):
    pass


# Properties to return to client
class AccountTransaction(AccountTransactionBase):
    id: Optional[int]
    party_id: int
    voucher_type: Optional[str]
    voucher_id: Optional[int]
    credit: Optional[Decimal]
    debit: Optional[Decimal]
    cheque_no: Optional[str]
    account_id: Optional[int]
    remarks: Optional[str]
    other_party_id: Optional[int]
    balance: Optional[Decimal]
    clearance_status: Optional[int]
    clearance_date: Optional[datetime]
    balance_type: Optional[int]
    date: Optional[datetime]
    created_from: Optional[int]
    created_by: Optional[int]
    bank_name: Optional[str]
    fyear: Optional[str] = None
    companyid: Optional[int] = None

    class Config:
        orm_mode = True
