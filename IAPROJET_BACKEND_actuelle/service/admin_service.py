from sqlalchemy.orm import Session
from models.Admin import Admin

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


def create_admin_service(db: Session, data):
    admin = Admin(
        nom=data.nom,
        prenom=data.prenom,
        numero=data.numero,
        adresse=data.adresse,
        mot_de_passe=hash_password(data.mot_de_passe)
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


def login_admin_service(db: Session, data):
    admin = db.query(Admin).filter(Admin.nom == data.nom).first()

    if not admin or not verify_password(data.mot_de_passe, admin.mot_de_passe):
        return None

    payload = {"sub": str(admin.id)}

    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer"
    }


def get_admin_service(db: Session, admin_id: str):
    return db.query(Admin).filter(Admin.id == admin_id).first()


def update_admin_service(db: Session, admin_id: str, data):
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        return None

    if data.nom:
        admin.nom = data.nom
    if data.mot_de_passe:
        admin.mot_de_passe = hash_password(data.mot_de_passe)

    db.commit()
    db.refresh(admin)
    return admin

