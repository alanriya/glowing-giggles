from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Pydantic defines the structure of the request and the response.
class QueryRequest(BaseModel):
    query: str
    
class CategoryQuery(BaseModel):
    category: str

class QueryResult(BaseModel):
    category: str
    page: str
    

    