from pydantic import BaseModel
from typing import Optional, List

class Tour(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    price: float
    location: str
    images: List[str] = []

    class Config:
        from_attributes = True