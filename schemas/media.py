from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class MediaBase(BaseModel):
    pass


# Properties to receive on item creation
class MediaCreate(MediaBase):
    image_id: Optional[str]
    type: Optional[str] = None
    image: Optional[str] = None
    created_date : Optional[datetime] = None

class MediaUpload(BaseModel):
    image_id: Optional[str]
    type: Optional[str] = None
    # image: Optional[str] = None
    created_date : Optional[datetime] = None

class MediaUpdate(MediaBase):
    type: Optional[str] = None
    image: Optional[str] = None
    created_date : Optional[datetime] = None
    pass

# Properties to return to client
class Media(MediaBase):
    image_id: Optional[str]
    type: Optional[str]
    image: Optional[str]
    created_date : Optional[datetime]
    class Config:
        orm_mode = True
