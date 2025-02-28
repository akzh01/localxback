from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Booking(BaseModel):
    id: Optional[str] = None
    user_id: str
    tour_id: str
    date: datetime
    status: str = "pending"  # По умолчанию статус "в ожидании"

    class Config:
        from_attributes = True  # Для работы с MongoDB