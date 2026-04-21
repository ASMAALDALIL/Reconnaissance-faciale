from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PresenceBase(BaseModel):
    employee_id: UUID
    camera_id: UUID

class PresenceCreate(PresenceBase):
    pass

class PresenceOut(PresenceBase):
    id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True
