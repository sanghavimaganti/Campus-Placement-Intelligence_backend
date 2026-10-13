from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Student
from app.schemas import LoginRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=UserResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    login_id = req.login_id.strip()
    password = req.password.strip()
    role_requested = (req.role or "student").lower()

    if role_requested == "admin":
        # Check Admin
        if login_id.lower() in ["admin@campus.edu", "admin", "tpo@campus.edu"] and password in ["admin123", "admin"]:
            return UserResponse(
                id=1,
                email="admin@campus.edu",
                name="Prof. Rajesh Varma (Head TPO)",
                role="admin",
                student_id=None,
                roll_number=None,
                department="Placement Cell",
                token="demo-tpo-auth-token-campus-placement-2026"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Admin credentials. Use admin@campus.edu / admin123"
            )

    # Student Login
    # Student can log in with roll number (e.g. '21CS001') or email ('aarav.sharma@campus.edu')
    student = db.query(Student).filter(
        or_(
            Student.roll_number.ilike(login_id),
            Student.email.ilike(login_id)
        )
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with roll number/email '{login_id}' not found in campus roster."
        )

    # Standard demo password accepted: student123 or roll number or password
    if password not in ["student123", "password", student.roll_number.lower(), "123456"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. For testing, use password: student123"
        )

    return UserResponse(
        id=student.id,
        email=student.email,
        name=student.name,
        role="student",
        student_id=student.id,
        roll_number=student.roll_number,
        department=student.department,
        token=f"student-auth-token-{student.roll_number}"
    )

@router.get("/demo-credentials")
def get_demo_credentials():
    return {
        "admin": {
            "login_id": "admin@campus.edu",
            "password": "admin123",
            "role_title": "Training & Placement Officer (TPO)"
        },
        "student": {
            "login_id": "21CS001",
            "password": "student123",
            "role_title": "Student Candidate (Aarav Sharma)"
        }
    }
