from sqlalchemy.orm import Session
from models.Departement import Departement
from schemas.departement import DepartementCreate

class DepartementService:

    @staticmethod
    def create(db: Session, data: DepartementCreate):
        departement = Departement(nom=data.nom)
        db.add(departement)
        db.commit()
        db.refresh(departement)
        return departement

    @staticmethod
    def get_all(db: Session):
        return db.query(Departement).all()

    @staticmethod
    def get_by_id(db: Session, departement_id: str):
        return db.query(Departement).filter(Departement.id == departement_id).first()

    @staticmethod
    def delete(db: Session, departement_id: str):
        dep = DepartementService.get_by_id(db, departement_id)
        if dep:
            db.delete(dep)
            db.commit()
        return dep
