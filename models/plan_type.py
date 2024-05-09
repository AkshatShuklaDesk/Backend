from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class PlanTypeBase(SQLModel):
    pass

class PlanTypeCreate(PlanTypeBase):
    pass

class PlanTypeUpdate(PlanTypeBase):
    pass

class PlanType(PlanTypeBase, table=True):
    __tablename__ = "plan_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
