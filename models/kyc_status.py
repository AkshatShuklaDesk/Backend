from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class KycStatusBase(SQLModel):
    pass

class KycStatusCreate(KycStatusBase):
    pass

class KycStatusUpdate(KycStatusBase):
    pass

class KycStatus(KycStatusBase, table=True):
    __tablename__ = "kyc_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
