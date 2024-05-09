from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class ChannelBase(SQLModel):
    pass

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(ChannelBase):
    pass

class Channel(ChannelBase, table=True):
    __tablename__ = "channel"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    invoice_no: Optional[str]
