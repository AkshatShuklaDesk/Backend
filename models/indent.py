from sqlalchemy import Boolean, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT,FLOAT
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime
from typing import Optional,Union
from sqlmodel import Field, SQLModel

class IndentBase(SQLModel):
    pass
class IndentCreate(IndentBase):
    pass

class IndentUpdate(IndentBase):
    pass

class Indent(IndentBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id : Optional[int]
    end_customer_loading_point_id : Optional[int]
    loading_point_id: Optional[int]
    destination_id :Optional[int]
    customer_id :Optional[int]
    end_customer_unloading_point_id :Optional[int]
    unloading_point_id: Optional[int]
    end_customer_id: Optional[int]
    customer_user_id: Optional[int]
    truck_type_id: Optional[str]
    ton: Optional[int]
    created_by: Optional[str]
    material_type_id: Optional[str]
    customer_price: Optional[int]
    trip_status_id: Optional[int]
    origin_id: Optional[int]
    pod_trip: Optional[str]  
    loading_unloading_points : Optional[str]
    pkgs : Optional[str]
    weight: Optional[int]
    pickupDate : Optional[str]
    weight_type : Optional[str]
    volumetric_weight : Optional[float]
    trip_status:Optional[int]
    actual_price:Optional[int]
    created_date:Optional[datetime]
    modified_date:Optional[datetime]
