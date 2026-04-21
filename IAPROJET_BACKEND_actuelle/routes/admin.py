from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from schemas.admin import AdminCreate, AdminLogin, AdminResponse, AdminUpdate
from service.admin_service import (
    create_admin_service,
    login_admin_service,
    get_admin_service,
    update_admin_service,
)
from core.security import decode_refresh_token, create_access_token, get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/", response_model=AdminResponse)
def create_admin(data: AdminCreate, db: Session = Depends(get_db)):
    return create_admin_service(db, data)


@router.post("/login/", response_model=dict)
def login(data: AdminLogin, db: Session = Depends(get_db)):
    result = login_admin_service(db, data)
    if not result:
        raise HTTPException(400, "Nom ou mot de passe incorrect")
    return result


@router.get("/{admin_id}/", response_model=AdminResponse)
def get_admin(admin_id: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    admin = get_admin_service(db, admin_id)
    if not admin:
        raise HTTPException(404, "Admin introuvable")
    return admin


@router.put("/{admin_id}/", response_model=AdminResponse)
def update_admin(admin_id: str, data: AdminUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    updated = update_admin_service(db, admin_id, data)
    if not updated:
        raise HTTPException(404, "Admin introuvable")
    return updated


@router.post("/refresh/", response_model=dict)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_refresh_token(refresh_token)
    except:
        raise HTTPException(401, "Refresh token invalide")

    admin_id = payload.get("sub")

    return {"access_token": create_access_token({"sub": admin_id})}
