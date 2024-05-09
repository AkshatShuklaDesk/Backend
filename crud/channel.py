from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.channel import Channel, ChannelCreate, ChannelBase


class CRUDChannel(CRUDBase[Channel, ChannelCreate, ChannelBase]):
    def get_all_channels(self,db:Session):
        channels = db.query(self.model).all()
        channels = jsonable_encoder(channels)
        return channels


channel = CRUDChannel(Channel)
