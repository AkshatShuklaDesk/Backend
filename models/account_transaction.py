import datetime

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Float,
    TIME,
    String,
    VARCHAR,
    DateTime,DATE
)
from sqlalchemy.dialects.mysql import DOUBLE
from db.session import Base


class AccountTransaction(Base):
    __tablename__ = "account_transaction"

    id = Column(Integer, primary_key=True, index=True)
    party_id = Column(Integer)
    voucher_type = Column(VARCHAR(10))
    voucher_id = Column(Integer)
    credit = Column(DOUBLE)
    debit = Column(DOUBLE)
    cheque_no = Column(VARCHAR(50))
    remarks = Column(VARCHAR(100))
    balance = Column(DOUBLE)
    clearance_status = Column(Integer)
    clearance_date = Column(DateTime)
    balance_type = Column(VARCHAR(10))
    date = Column(DateTime)
    unique_id = Column(Integer)
    other_party_id = Column(Integer)
    account_id = Column(Integer)
    created_from = Column(Integer)
    created_by = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.now())
    modified_date = Column(DateTime, default=datetime.datetime.now())
    bank_name = Column(VARCHAR(50))
    fyear = Column(VARCHAR(10))
    companyid = Column(Integer)

