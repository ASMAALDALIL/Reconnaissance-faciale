from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from database import Base

class Employee(Base):
    __tablename__ = "employee"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_complet = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    adresse= Column(String, nullable=False)
    path_dossier_images = Column(String, nullable=False)
    departement_id = Column(UUID(as_uuid=True), ForeignKey("departement.id"), nullable=False)
