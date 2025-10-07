from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationInDB(BaseModel):
    id: int
    user_id: int
    type: str
    message: str
    related_id: Optional[int]
    related_username: Optional[str]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True