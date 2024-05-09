
# class User(Base):

#     __tablename__ = "user"

#     id = Column(Integer,primary_key=True)
#     username = Column(VARCHAR(80))
#     password = Column(VARCHAR(100))
#     is_admin = Column(Boolean,default=False)
#     mobile_no = Column(VARCHAR(10))
#     company_id = Column(Integer,ForeignKey(Company.id))
#     is_active = Column(Boolean,default=False)
#     mail_id = Column(VARCHAR(255),unique=True)
#     created_at = Column(DateTime,default=datetime.datetime.now())
#     modified_at = Column(DateTime,default=datetime.datetime.now())


from typing import Optional,List
from pydantic import BaseModel


# Shared properties
class UserBase(BaseModel):
    class Config:
        orm_mode = True


# Properties to return to client
class User(UserBase):
    id: int
    first_name:str
    last_name:str
    password:str
    is_admin:int = 0
    contact_no:str
    company_id:int
    is_active:bool = 1
    email_address:str 




class UserCreate(UserBase):
    first_name:str
    last_name:str
    password:str
    is_admin:int = 0
    contact_no:str
    company_id:int
    is_active:bool = 1
    email_address:str 


class UserReturnResponse(UserBase):
    first_name:str    
    is_admin:int
    contact_no:str
    is_active:bool
    email_address:str 