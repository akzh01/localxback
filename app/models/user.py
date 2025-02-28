from pydantic import BaseModel, EmailStr
from typing import Optional
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
