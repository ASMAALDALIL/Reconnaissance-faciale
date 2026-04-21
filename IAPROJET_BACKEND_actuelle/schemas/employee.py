
from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class EmployeeBase(BaseModel):
    nom_complet: str
    path_dossier_images: str
    numero :str
    adresse:str
class EmployeeCreate(EmployeeBase):
    departement_id: UUID

class EmployeeOut(EmployeeBase):
    id: UUID
    departement_id: UUID

    class Config:
        from_attributes = True




