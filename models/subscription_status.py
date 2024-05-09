from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from enum import Enum
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class SubscriptionStatusBase(SQLModel):
    pass

class SubscriptionStatusCreate(SubscriptionStatusBase):
    pass

class SubscriptionStatusUpdate(SubscriptionStatusBase):
    pass

class SubscriptionStatus(SubscriptionStatusBase, table=True):
    __tablename__ = "subscription_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
