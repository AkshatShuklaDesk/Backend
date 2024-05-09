from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT,FLOAT
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime
from typing import Optional, Union
from sqlmodel import Field, SQLModel

class ProductBase(SQLModel):
    pass

class ProductCreate(ProductBase):
    name: str
    hsn_code: Optional[str]
    sku: Optional[str]
    tax_rate: Optional[float]
    discount: Optional[float]
    description: Optional[str]
    category: Optional[str]

class ProductUpdate(ProductBase):
    name: str
    hsn_code: Optional[str]
    sku: Optional[str]
    tax_rate: Optional[float]
    discount: Optional[float]
    description: Optional[str]
    category: Optional[str]

class Product(ProductBase, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    hsn_code: Optional[str]
    sku: Optional[str]
    tax_rate: Optional[float]
    discount: Optional[float]
    description: Optional[str]
    category: Optional[str]
    img_1: Optional[str]
    img_2: Optional[str]
    length_img: Optional[str]
    width_img: Optional[str]
    height_img: Optional[str]
    weight_img: Optional[str]
    weighing_scale_img: Optional[str]
    with_label_img: Optional[str]
    created_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    modified_by: Union[int, None] = Field(
        default=None, foreign_key="users.id"
    )
    created_date: Optional[datetime]
    modified_date: Optional[datetime]
    length : Optional[float]
    width : Optional[float]
    height : Optional[float]
    volumetric_weight : Optional[float]
    cod_charge : Optional[float]
    unit_price : Optional[float]