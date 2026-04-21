from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database import Base

class Presence(Base):
    __tablename__ = "presence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("camera.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)  # date + heure d’entrée
