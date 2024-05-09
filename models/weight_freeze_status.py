from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class WeightFreezeStatusBase(SQLModel):
    pass

class WeightFreezeStatusCreate(WeightFreezeStatusBase):
    pass

class WeightFreezeStatusUpdate(WeightFreezeStatusBase):
    pass

class WeightFreezeStatus(WeightFreezeStatusBase, table=True):
    __tablename__ = "weight_freeze_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
