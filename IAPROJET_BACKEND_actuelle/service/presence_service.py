from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy import Date
from io import BytesIO
import pandas as pd
from models.Presence import Presence
from models.Camera import Camera
from models.Employe import Employee
from schemas.presence import PresenceCreate
class PresenceService:

    @staticmethod
    def enregistrer_presence(db: Session, data: PresenceCreate):

        camera = db.query(Camera).filter(Camera.id == data.camera_id).first()
        if not camera or not camera.is_entry_camera:
            return None, "Camera introuvable ou ne valide pas les présences"

        # Vérifier doublon dans la même journée
        existing = db.query(Presence).filter(
            Presence.employee_id == data.employee_id,
            Presence.timestamp.cast(Date) == date.today()
        ).first()

        if existing:
            return None, "Présence déjà enregistrée aujourd'hui"

        presence = Presence(
            employee_id=data.employee_id,
            camera_id=data.camera_id,
            timestamp=datetime.now()
        )
        db.add(presence)
        db.commit()
        db.refresh(presence)

        return presence, None

    @staticmethod
    def get_absents_semaine(db: Session):
        today = date.today()
        start_week = today - timedelta(days=today.weekday())
        present_ids = [
            p[0] for p in db.query(Presence.employee_id)
            .filter(Presence.timestamp.cast(Date) >= start_week).all()
        ]
        return db.query(Employee).filter(~Employee.id.in_(present_ids)).all()
    @staticmethod
    def get_absents_mois(db: Session):
        today = date.today()
        start_month = today.replace(day=1)
        present_ids = [
            p[0] for p in db.query(Presence.employee_id)
            .filter(Presence.timestamp.cast(Date) >= start_month).all()
        ]
        return db.query(Presence).filter(~Employee.id.in_(present_ids)).all()

    @staticmethod
    def get_absents_jour(db: Session):
        today = date.today()

        present_ids = [
            p[0] for p in db.query(Presence.employee_id)
            .filter(Presence.timestamp.cast(Date) == today).all()
        ]

        return db.query(Employee).filter(~Employee.id.in_(present_ids)).all()

    @staticmethod
    def export_absents_excel(db: Session):
        absents = PresenceService.get_absents_jour(db)
        data = [{"Nom": e.nom} for e in absents]

        df = pd.DataFrame(data)
        stream = BytesIO()
        df.to_excel(stream, index=False)
        stream.seek(0)

        return stream
    @staticmethod
    def get_absence_departement(db:Session,departement_id:UUID,target_date:Date):
        if target_date is None:
            target_date = date.today()

        present_ids = [
            p[0] for p in db.query(Presence.employee_id)
            .filter(Presence.timestamp.cast(Date) == target_date).all()
        ]
        absents=db.query(Employee).filter(
            Employee.departement_id==departement_id,
            ~Employee.id.in_(present_ids)
        ).all()

        return absents
    @staticmethod
    def get_absence_par_date(db: Session, target_date: date):

        present_ids = [
            p[0] for p in db.query(Presence.employee_id)
            .filter(Presence.timestamp.cast(Date) == target_date)
            .all()
        ]

        absents = db.query(Employee).filter(
            ~Employee.id.in_(present_ids)
        ).all()

        return absents

