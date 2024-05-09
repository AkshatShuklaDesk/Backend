from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class WeightFreezeBase(SQLModel):
    pass

class Image(BaseModel):
    img_1: Optional[str] = None
    img_2: Optional[str] = None
    length_img: Optional[str] = None
    width_img: Optional[str] = None
    height_img: Optional[str] = None
    weight_img: Optional[str] = None

class WeightFreezeCreate(WeightFreezeBase):
    product_id: Optional[int] = None
    status_name: Optional[str] = None
    product_category: Optional[str] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    chargeable_weight: Optional[float] = None
    images: Optional[Image] = None

class WeightFreezeUpdate(WeightFreezeBase):
    pass

class WeightFreeze(WeightFreezeBase, table=True):
    __tablename__ = "weight_freeze"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Union[int, None] = Field(
        default=None, foreign_key="product.id"
    )
    status_id: Union[int, None] = Field(
        default=None, foreign_key="weight_freeze_status.id"
    )
    product_category: Optional[str]
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]
    weight: Optional[float]
    chargeable_weight: Optional[float]
    created_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    modified_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
