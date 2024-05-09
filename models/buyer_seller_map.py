from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class BuyerSellerMapBase(SQLModel):
    pass

class BuyerSellerMapCreate(BuyerSellerMapBase):
    name: str
    gst: str
    pass

class BuyerSellerMapUpdate(BuyerSellerMapBase):
    pass

class BuyerSellerMap(BuyerSellerMapBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    seller_id: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
