from typing import Optional
from sqlmodel import Field, SQLModel

class PartnerBase(SQLModel):
    pass

class PartnerCreate(PartnerBase):
    pass

class PartnerUpdate(PartnerBase):
    pass

class Partner(PartnerBase, table=True):
    __tablename__ = "partner"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
