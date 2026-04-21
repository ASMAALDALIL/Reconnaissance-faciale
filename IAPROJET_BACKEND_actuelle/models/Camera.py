from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class Camera(Base):
    __tablename__ = "camera"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String, nullable=False)
    rtsp_url = Column(String, nullable=True)
    departement_id = Column(UUID(as_uuid=True), ForeignKey("departement.id"), nullable=False)
    is_entry_camera = Column(Boolean, default=False)

    departement = relationship("Departement", back_populates="cameras")
