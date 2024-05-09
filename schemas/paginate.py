from typing import Optional,List,Dict

from pydantic import BaseModel


# Shared properties
class Paginate(BaseModel):
    number_of_rows: int
    page_number: int