from pydantic import BaseModel


# Shared properties
class CompanyBase(BaseModel):
    class Config:
        orm_mode = True


class Company(CompanyBase):
    name:str
    gst:str
    password:str
    contact:int
    email:str
    address: str




class CompanyCreate(CompanyBase):
    name: str
    gst: str
    password: str
    contact: int
    email: str
    address: str



