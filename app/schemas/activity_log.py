from pydantic import BaseModel
from datetime import datetime

class ActivityLogBase(BaseModel):
    note_id: int
    user_id: int
    action: str
    timestamp: datetime

class ActivityLog(ActivityLogBase):
    id: int

    class Config:
        orm_mode = True