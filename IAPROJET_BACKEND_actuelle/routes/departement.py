from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from service.departement_service import DepartementService
from schemas.departement import DepartementCreate, DepartementOut
from core.security import get_current_admin

router = APIRouter(
    prefix="/departements",
    tags=["Departements"]
)


@router.post("/", response_model=DepartementOut)
def add_departement(
    data: DepartementCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return DepartementService.create(db, data)


@router.get("/", response_model=list[DepartementOut])
def list_departements(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return DepartementService.get_all(db)


@router.get("/{departement_id}", response_model=DepartementOut)
def get_departement(
    departement_id: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    dep = DepartementService.get_by_id(db, departement_id)
    if not dep:
        raise HTTPException(404, "Département introuvable")
    return dep


@router.delete("/{departement_id}")
def delete_departement(
    departement_id: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    dep = DepartementService.delete(db, departement_id)
    if not dep:
        raise HTTPException(404, "Département introuvable")
    return {"message": "Département supprimé"}
