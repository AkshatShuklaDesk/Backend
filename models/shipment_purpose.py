from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class ShipmentPurposeBase(SQLModel):
    pass

class ShipmentPurposeCreate(ShipmentPurposeBase):
    pass

class ShipmentPurposeUpdate(ShipmentPurposeBase):
    pass

class ShipmentPurpose(ShipmentPurposeBase, table=True):
    __tablename__ = "shipment_purpose"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
