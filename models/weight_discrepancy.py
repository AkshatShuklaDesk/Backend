from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT
from sqlalchemy.orm import relationship
from db.session import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class WeightDiscrepancyBase(SQLModel):
    pass

class WeightDiscrepancyCreate(WeightDiscrepancyBase):
    status_id: Optional[int] = None
    status_name: Optional[str] = None
    charged_weight: Optional[float] = None
    excess_weight: Optional[float] = None
    excess_rate: Optional[float] = None
    courier_image: Optional[str] = None
    pass

class WeightDiscrepancyDispute(WeightDiscrepancyBase):
    product_id: Optional[int]
    length_img: Optional[str] = None
    width_img: Optional[str] = None
    height_img: Optional[str] = None
    weight_img: Optional[str] = None
    category: Optional[str] = None
    weighing_scale_img: Optional[str] = None
    with_label_img: Optional[str] = None
    pass

class WeightDiscrepancyUpdate(WeightDiscrepancyBase):
    pass

class WeightDiscrepancy(WeightDiscrepancyBase, table=True):
    __tablename__ = "weight_discrepancy"
    # id, order_id, charged_weight, excess_weight, excess_rate, status, generation_date, modified_date, courier_image
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Union[int, None] = Field(
        default=None, foreign_key="order.id"
    )
    status_id: Union[int, None] = Field(
        default=None, foreign_key="weight_discrepancy_status.id"
    )
    charged_weight: Optional[float]
    excess_weight: Optional[float]
    excess_rate: Optional[float]
    courier_image: Optional[str]
    created_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    modified_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    generation_date: Optional[datetime]
    modified_date: Optional[datetime]
