from sqlalchemy.orm import Session
from uuid import UUID
from models.Employe import Employee
from schemas.employee import EmployeeCreate

class EmployeeService:

    @staticmethod
    def get_all(db: Session):
        return db.query(Employee).all()

    @staticmethod
    def get_by_id(db: Session, employee_id: UUID):
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def create(db: Session, data: EmployeeCreate):
        employee = Employee(**data.dict())
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def delete(db: Session, employee_id: UUID):
        employee = EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None

        db.delete(employee)
        db.commit()
        return True

    @staticmethod
    def update(db: Session, employee_id: UUID, data: EmployeeCreate):
        employee = EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None

        for field, value in data.dict().items():
            setattr(employee, field, value)

        db.commit()
        db.refresh(employee)
        return employee
