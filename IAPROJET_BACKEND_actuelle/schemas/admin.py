import uuid
from pydantic import BaseModel

class AdminBase(BaseModel):
    nom: str
    prenom:str
    adresse:str
    numero:str
class AdminCreate(AdminBase):
    nom: str
    prenom: str
    adresse: str
    numero: str
    mot_de_passe: str

class AdminLogin(BaseModel):
    nom: str
    mot_de_passe: str

class AdminUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    adresse: str | None = None
    numero: str | None = None
    mot_de_passe: str | None = None

class AdminResponse(BaseModel):
    id: uuid.UUID
    nom: str
    prenom: str
    adresse: str
    numero: str
    mot_de_passe: str
    model_config = {
        "from_attributes": True
    }
