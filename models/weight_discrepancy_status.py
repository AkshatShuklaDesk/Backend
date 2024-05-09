from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class WeightDiscrepancyStatusBase(SQLModel):
    pass

class WeightDiscrepancyStatusCreate(WeightDiscrepancyStatusBase):
    pass

class WeightDiscrepancyStatusUpdate(WeightDiscrepancyStatusBase):
    pass

class WeightDiscrepancyStatus(WeightDiscrepancyStatusBase, table=True):
    __tablename__ = "weight_discrepancy_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
