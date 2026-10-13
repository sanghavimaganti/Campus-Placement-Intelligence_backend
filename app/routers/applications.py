import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, CompanyDrive, DriveApplication
from app.schemas import ApplicationCreate, ApplicationResponse
from app.analytics import evaluate_student_eligibility, calculate_readiness_score

router = APIRouter(prefix="/applications", tags=["Drive Applications"])

@router.post("/apply", response_model=ApplicationResponse, status_code=201)
def apply_to_company_drive(req: ApplicationCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    company = db.query(CompanyDrive).filter(CompanyDrive.id == req.company_drive_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company drive not found")

    # Check if already applied
    existing = db.query(DriveApplication).filter(
        DriveApplication.student_id == req.student_id,
        DriveApplication.company_drive_id == req.company_drive_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this company drive.")

    # Validate eligibility criteria
    criteria = {
        "min_cgpa": company.min_cgpa,
        "min_tenth_percentage": company.min_tenth_percentage,
        "min_twelfth_percentage": company.min_twelfth_percentage,
        "max_active_backlogs": company.max_active_backlogs,
        "max_history_backlogs": company.max_history_backlogs,
        "eligible_branches": [b.strip() for b in company.eligible_branches.split(",") if b.strip()],
        "required_skills": [s.strip() for s in company.required_skills.split(",") if s.strip()]
    }
    is_elig, reasons, _, _, _ = evaluate_student_eligibility(student, criteria)
    if not is_elig:
        raise HTTPException(
            status_code=400,
            detail=f"Candidate ineligible for {company.company_name}: {'; '.join(reasons)}"
        )

    new_app = DriveApplication(
        student_id=req.student_id,
        company_drive_id=req.company_drive_id,
        status="Applied",
        applied_at=datetime.datetime.utcnow()
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return ApplicationResponse(
        id=new_app.id,
        student_id=new_app.student_id,
        company_drive_id=new_app.company_drive_id,
        company_name=company.company_name,
        role=company.role,
        package_lpa=company.package_lpa,
        status=new_app.status,
        applied_at=new_app.applied_at.strftime("%Y-%m-%d %H:%M")
    )

@router.get("/student/{student_id}", response_model=List[ApplicationResponse])
def get_student_applications(student_id: int, db: Session = Depends(get_db)):
    apps = db.query(DriveApplication).filter(DriveApplication.student_id == student_id).all()
    results = []
    for a in apps:
        comp = db.query(CompanyDrive).filter(CompanyDrive.id == a.company_drive_id).first()
        if comp:
            results.append(ApplicationResponse(
                id=a.id,
                student_id=a.student_id,
                company_drive_id=a.company_drive_id,
                company_name=comp.company_name,
                role=comp.role,
                package_lpa=comp.package_lpa,
                status=a.status,
                applied_at=a.applied_at.strftime("%Y-%m-%d %H:%M") if a.applied_at else "Recently"
            ))
    return results

@router.get("/company/{company_id}")
def get_company_applicants(company_id: int, db: Session = Depends(get_db)):
    comp = db.query(CompanyDrive).filter(CompanyDrive.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company drive not found")

    apps = db.query(DriveApplication).filter(DriveApplication.company_drive_id == company_id).all()
    results = []
    for a in apps:
        student = db.query(Student).filter(Student.id == a.student_id).first()
        if student:
            readiness = calculate_readiness_score(student)
            results.append({
                "application_id": a.id,
                "student_id": student.id,
                "roll_number": student.roll_number,
                "name": student.name,
                "department": student.department,
                "cgpa": student.cgpa,
                "active_backlogs": student.active_backlogs,
                "skills": student.skills,
                "readiness_score": readiness,
                "status": a.status,
                "applied_at": a.applied_at.strftime("%Y-%m-%d %H:%M") if a.applied_at else ""
            })
    return {
        "company_name": comp.company_name,
        "role": comp.role,
        "total_applicants": len(results),
        "applicants": results
    }
