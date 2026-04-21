from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
from core.security import get_current_admin
from database import get_db
from schemas.employee import EmployeeCreate, EmployeeOut
from service.employee_service import EmployeeService
from models.Employe import  Employee
import os
from sqlalchemy import func
router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeOut])
def get_employees(db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    return EmployeeService.get_all(db)

@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: UUID, db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employé introuvable")
    return employee

@router.post("/", response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    return EmployeeService.create(db, data)

@router.delete("/{employee_id}")
def delete_employee(employee_id: UUID, db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    deleted = EmployeeService.delete(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employé introuvable")
    return {"message": "Employé supprimé"}

@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: UUID, data: EmployeeCreate, db: Session = Depends(get_db),admin=Depends(get_current_admin)):
    employee = EmployeeService.update(db, employee_id, data)
    if not employee:
        raise HTTPException(status_code=404, detail="Employé introuvable")
    return employee
'''add router export photo'''
##UPLOAD_DIR = r"C:\Users\HP\PycharmProjects\IAPROJET_BACKEND_actuelle\AI\dataset" dyal assma
UPLOAD_DIR = r"C:\Users\pc\OneDrive\Documents\projet_ai_officiel\IAPROJET_BACKEND_actuelle\AI\dataset"


os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{employee_id}/upload-photo")
def upload_employee_photo(
    employee_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):

   
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(404, "Employé introuvable")

   
    full_name = f"{employee.prenom}_{employee.nom}".replace(" ", "_")

    employee_folder = os.path.join(UPLOAD_DIR, full_name)
    os.makedirs(employee_folder, exist_ok=True)

    filename = file.filename
    file_path = os.path.join(employee_folder, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())


    if not employee.path_dossier_images:
        employee.path_dossier_images = employee_folder
        db.commit()
        db.refresh(employee)

    return {"message": "Photo uploadée avec succès", "path": file_path}
'''ajouter pour AI'''


@router.get("/by-name/{name}", response_model=EmployeeOut)
def get_by_name(name: str, db: Session = Depends(get_db)):
    # Transforme le nom pour correspondre aux deux formats
    clean_name_underscore = name.lower()          # ex: "angelina_jolie"
    clean_name_space = name.replace("_", " ").lower()  # ex: "angelina jolie"

    employee = db.query(Employee).filter(
        (func.lower(Employee.nom_complet) == clean_name_underscore) |
        (func.lower(Employee.nom_complet) == clean_name_space)
    ).first()

    if not employee:
        all_names = [e.nom_complet for e in db.query(Employee).all()]
        print("Tous les noms en DB:", all_names)
        raise HTTPException(404, "Employee not found")

    return employee

