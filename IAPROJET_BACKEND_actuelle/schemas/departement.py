from pydantic import BaseModel
from uuid import UUID

class DepartementBase(BaseModel):
    nom: str

class DepartementCreate(DepartementBase):
    pass

class DepartementOut(DepartementBase):
    id: UUID

    class Config:
        from_attributes = True
