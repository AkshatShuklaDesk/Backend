from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class CompanyBase(SQLModel):
    pass

class CompanyCreate(CompanyBase):
    name: str
    gst: str
    pass

class CompanyUpdate(CompanyBase):
    pass

class Company(CompanyBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    gst: Optional[str]
    email : Optional[str]
    password : Optional[str]
    address : Optional[str]
    contact : Optional[int]
    otp : Optional[int]
    is_admin : Optional[int] = Field(default=1)
    wallet_balance:Optional[int]=Field(default=0)
    kyc_status_id:Optional[int]=Field(default=1)
    users_type_id: Union[int, None] = Field(
        default=2, foreign_key="users_type.id"
    )
