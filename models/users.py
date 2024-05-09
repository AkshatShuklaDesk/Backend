from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel
from datetime import datetime

class UsersBase(SQLModel):
    pass

class UsersCreate(UsersBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: Optional[str] = None
    contact_no: Optional[str] = None
    password: Optional[str] = None
    company_id:Optional[str]=None
    users_type_id: Optional[int] = None


class UsersUpdate(UsersBase):
    pass

class Users(UsersBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: Optional[str]
    last_name: Optional[str]
    email_address: Optional[str]
    contact_no: Optional[str]
    is_active: Optional[bool] = Field(default=1)
    alternate_contact_no: Optional[str]
    company_id: Union[int, None] = Field(
        default=None, foreign_key="company.id"
    )
    plan_type_id: Union[int, None] = Field(
        default=None, foreign_key="plan_type.id"
    )
    subscription_status_id: Union[int, None] = Field(
        default=None, foreign_key="subscription_status.id"
    )
    subscription_span: Optional[str]
    kyc_status_id: Union[int, None] = Field(
        default=1, foreign_key="kyc_status.id"
    )
    total_order_ship_monthly: Optional[int]
    users_type_id: Union[int, None] = Field(
        default=1, foreign_key="users_type.id"
    )
    wallet_balance: Optional[int]=Field(default=0)
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
    is_admin:Optional[int]=Field(default=0)
    requested_balance:Optional[float]=Field(default=0)
