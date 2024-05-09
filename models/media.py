from sqlalchemy import Boolean, ForeignKey, Integer, String, VARCHAR, DateTime,TEXT,FLOAT
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime
from typing import Optional,Union
from sqlmodel import Field, SQLModel


class Mediabase(SQLModel):
    pass
class MediaCreate(Mediabase):
    pass

class MediaUpdate(Mediabase):
    pass

class Media(Mediabase,table=True):
    id: Optional[int] = Field( default=None,primary_key=True)
    image_id :str
    type :str
    image : str
    created_date : datetime
