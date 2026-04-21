# -*- coding: utf-8 -*-
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String
import uuid
from database import Base
class Admin(Base):
    __tablename__="admin"
    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    prenom=Column(String,nullable=False)
    nom=Column(String,nullable=False)
    numero  = Column(String, nullable=False)
    adresse = Column(String, nullable=False)
    mot_de_passe=Column(String,nullable=False)