from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CameraBase(BaseModel):
    numero: str
    rtsp_url: Optional[str] = None
    departement_id: UUID
    is_entry_camera: bool = False

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    id: UUID

    class Config:
        orm_mode = True
