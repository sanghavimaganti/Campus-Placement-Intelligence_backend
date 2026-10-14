import io
import csv
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Student, CompanyDrive, User
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app.analytics import calculate_readiness_score, evaluate_student_eligibility

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=List[StudentResponse])
def get_students(
    search: Optional[str] = Query(None, description="Search by name or roll number"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by placement status"),
    min_cgpa: Optional[float] = Query(None, description="Filter by minimum CGPA"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Student)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(or_(Student.name.ilike(search_filter), Student.roll_number.ilike(search_filter)))

    if department and department != "All":
        query = query.filter(Student.department == department)

    if status and status != "All":
        query = query.filter(Student.placement_status == status)

    if min_cgpa is not None:
        query = query.filter(Student.cgpa >= min_cgpa)

    students = query.order_by(Student.cgpa.desc()).offset(skip).limit(limit).all()

    # Attach computed readiness_score
    results = []
    for s in students:
        s_dict = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        s_dict["readiness_score"] = calculate_readiness_score(s)
        results.append(StudentResponse(**s_dict))

    return results

@router.get("/{student_id}")
def get_student_detail(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    readiness = calculate_readiness_score(student)
    
    # Check which company drives this student is eligible for
    drives = db.query(CompanyDrive).all()
    eligible_drives = []
    for drive in drives:
        criteria = {
            "min_cgpa": drive.min_cgpa,
            "min_tenth_percentage": drive.min_tenth_percentage,
            "min_twelfth_percentage": drive.min_twelfth_percentage,
            "max_active_backlogs": drive.max_active_backlogs,
            "max_history_backlogs": drive.max_history_backlogs,
            "eligible_branches": [b.strip() for b in drive.eligible_branches.split(",") if b.strip()],
            "required_skills": [s.strip() for s in drive.required_skills.split(",") if s.strip()]
        }
        is_elig, reasons, match_pct, matched, missing = evaluate_student_eligibility(student, criteria)
        eligible_drives.append({
            "drive_id": drive.id,
            "company_name": drive.company_name,
            "role": drive.role,
            "tier": drive.tier,
            "package_lpa": drive.package_lpa,
            "is_eligible": is_elig,
            "reasons": reasons,
            "skill_match_percentage": match_pct
        })

    s_dict = {c.name: getattr(student, c.name) for c in student.__table__.columns}
    s_dict["readiness_score"] = readiness
    s_dict["eligible_drives"] = eligible_drives
    return s_dict

@router.post("", response_model=StudentResponse, status_code=201)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(
        or_(Student.roll_number == student_in.roll_number, Student.email == student_in.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this roll number or email already exists")

    new_student = Student(**student_in.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    s_dict = {c.name: getattr(new_student, c.name) for c in new_student.__table__.columns}
    s_dict["readiness_score"] = calculate_readiness_score(new_student)
    return StudentResponse(**s_dict)

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_in: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = student_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    # Sync linked User record if name or email changed
    if "name" in update_data or "email" in update_data:
        linked_user = db.query(User).filter(
            or_(User.student_id == student.id, User.email.ilike(student.email))
        ).first()
        if linked_user:
            if "name" in update_data and update_data["name"]:
                linked_user.name = update_data["name"]
            if "email" in update_data and update_data["email"]:
                linked_user.email = update_data["email"]

    db.commit()
    db.refresh(student)

    s_dict = {c.name: getattr(student, c.name) for c in student.__table__.columns}
    s_dict["readiness_score"] = calculate_readiness_score(student)
    return StudentResponse(**s_dict)

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": f"Student '{student.roll_number}' successfully deleted"}

@router.post("/upload-csv")
async def upload_students_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV or Excel file")

    content = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    # Standardize columns
    column_mapping = {
        "roll_no": "roll_number",
        "rollno": "roll_number",
        "roll number": "roll_number",
        "student_name": "name",
        "student name": "name",
        "branch": "department",
        "dept": "department",
        "10th": "tenth_percentage",
        "10th_percentage": "tenth_percentage",
        "12th": "twelfth_percentage",
        "12th_percentage": "twelfth_percentage",
        "backlogs": "active_backlogs",
        "active backlogs": "active_backlogs",
        "status": "placement_status"
    }

    df.rename(columns=lambda c: column_mapping.get(c.strip().lower(), c.strip().lower()), inplace=True)

    required_cols = ["roll_number", "name", "department", "cgpa", "tenth_percentage", "twelfth_percentage"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"Missing required columns in CSV: {', '.join(missing_cols)}")

    imported_count = 0
    updated_count = 0

    for _, row in df.iterrows():
        roll = str(row["roll_number"]).strip()
        email = str(row.get("email", f"{roll.lower()}@campus.edu")).strip()
        
        student = db.query(Student).filter(Student.roll_number == roll).first()
        data = {
            "roll_number": roll,
            "name": str(row["name"]).strip(),
            "email": email,
            "gender": str(row.get("gender", "Other")).strip().capitalize(),
            "department": str(row["department"]).strip().upper(),
            "cgpa": float(row["cgpa"]),
            "tenth_percentage": float(row["tenth_percentage"]),
            "twelfth_percentage": float(row["twelfth_percentage"]),
            "active_backlogs": int(row.get("active_backlogs", 0)),
            "history_of_backlogs": int(row.get("history_of_backlogs", row.get("active_backlogs", 0))),
            "skills": str(row.get("skills", "")).strip(),
            "projects_count": int(row.get("projects_count", 0)),
            "internships_count": int(row.get("internships_count", 0)),
            "certifications_count": int(row.get("certifications_count", 0)),
            "placement_status": str(row.get("placement_status", "Unplaced")).strip(),
            "placed_company": str(row.get("placed_company", "")) if pd.notna(row.get("placed_company")) else None,
            "package_lpa": float(row.get("package_lpa", 0.0)) if pd.notna(row.get("package_lpa")) and row.get("package_lpa") else None
        }

        if student:
            for k, v in data.items():
                setattr(student, k, v)
            updated_count += 1
        else:
            new_student = Student(**data)
            db.add(new_student)
            imported_count += 1

    db.commit()
    return {
        "message": f"Successfully processed {len(df)} records.",
        "imported_new": imported_count,
        "updated_existing": updated_count
    }

@router.get("/sample-csv/download")
def download_sample_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "roll_number", "name", "email", "gender", "department", "cgpa",
        "tenth_percentage", "twelfth_percentage", "active_backlogs",
        "history_of_backlogs", "skills", "projects_count",
        "internships_count", "certifications_count", "placement_status"
    ])
    writer.writerow([
        "21CS099", "Devansh Patel", "devansh.patel@campus.edu", "Male", "CSE", 8.45,
        85.5, 87.0, 0, 0, "Python, SQL, React, Docker", 2, 1, 1, "Unplaced"
    ])
    writer.writerow([
        "21EC088", "Riya Sharma", "riya.sharma@campus.edu", "Female", "ECE", 7.9,
        82.0, 80.5, 0, 0, "C, Embedded Systems, Python, Verilog", 2, 1, 1, "Unplaced"
    ])
    
    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sample_placement_students.csv"}
    )
