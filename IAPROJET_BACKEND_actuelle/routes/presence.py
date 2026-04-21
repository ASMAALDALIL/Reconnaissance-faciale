from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID

from schemas.employee import EmployeeOut
from database import get_db
from service.presence_service import PresenceService
from schemas.presence import PresenceCreate, PresenceOut
from core.security import get_current_admin

router = APIRouter(prefix="/presence", tags=["Presence"])

# 1. ROUTE POUR L'INTELLIGENCE ARTIFICIELLE (POST)
@router.post("/", response_model=PresenceOut)
def enregistrer_presence(data: PresenceCreate, db: Session = Depends(get_db)):
    presence, error = PresenceService.enregistrer_presence(db, data)
    if error:
        print("⚠️ Erreur enregistrement :", error)
        raise HTTPException(status_code=400, detail=error)
    return presence

# 2. ROUTE UNIQUE POUR LE FRONTEND (GET ABSENTS)
@router.get("/absents", response_model=list[EmployeeOut])
def absents_unified(
    mode: str = Query("day"),          # day, week, month
    target_date: date | None = Query(None), # YYYY-MM-DD
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    mode = mode.lower()

    if mode == "week":
        return PresenceService.get_absents_semaine(db)
    elif mode == "month":
        return PresenceService.get_absents_mois(db)
    elif mode == "day":
        if not target_date or target_date == date.today():
            return PresenceService.get_absents_jour(db)
        return PresenceService.get_absence_par_date(db, target_date)
    else:
        raise HTTPException(400, "Mode invalide (day, week, month)")

# 3. ROUTE FILTRE PAR DÉPARTEMENT
@router.get("/absents/departement/{departement_id}", response_model=list[EmployeeOut])
def absents_departement(
    departement_id: UUID,
    target_date: date | None = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return PresenceService.get_absence_departement(db, departement_id, target_date)
