from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, CompanyDrive
from app.analytics import generate_analytics_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_placement_summary(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    companies = db.query(CompanyDrive).all()
    return generate_analytics_summary(students, companies)
