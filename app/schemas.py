from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Student Schemas ---
class StudentBase(BaseModel):
    roll_number: str
    name: str
    email: str
    gender: Optional[str] = "Other"
    department: str
    cgpa: float = Field(..., ge=0.0, le=10.0)
    tenth_percentage: float = Field(..., ge=0.0, le=100.0)
    twelfth_percentage: float = Field(..., ge=0.0, le=100.0)
    active_backlogs: int = Field(default=0, ge=0)
    history_of_backlogs: int = Field(default=0, ge=0)
    skills: Optional[str] = ""
    projects_count: Optional[int] = 0
    internships_count: Optional[int] = 0
    certifications_count: Optional[int] = 0
    placement_status: Optional[str] = "Unplaced"
    placed_company: Optional[str] = None
    package_lpa: Optional[float] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    cgpa: Optional[float] = None
    tenth_percentage: Optional[float] = None
    twelfth_percentage: Optional[float] = None
    active_backlogs: Optional[int] = None
    history_of_backlogs: Optional[int] = None
    skills: Optional[str] = None
    projects_count: Optional[int] = None
    internships_count: Optional[int] = None
    certifications_count: Optional[int] = None
    placement_status: Optional[str] = None
    placed_company: Optional[str] = None
    package_lpa: Optional[float] = None

class StudentResponse(StudentBase):
    id: int
    readiness_score: Optional[float] = 0.0

    class Config:
        from_attributes = True

# --- Company Drive Schemas ---
class CompanyDriveBase(BaseModel):
    company_name: str
    role: str
    tier: Optional[str] = "Dream"
    package_lpa: float
    min_cgpa: float = 7.0
    min_tenth_percentage: float = 60.0
    min_twelfth_percentage: float = 60.0
    max_active_backlogs: int = 0
    max_history_backlogs: int = 1
    eligible_branches: str = "CSE,IT,ECE"
    required_skills: str = "Python,SQL"
    drive_date: Optional[str] = ""
    registration_deadline: Optional[str] = ""
    status: Optional[str] = "Upcoming"

class CompanyDriveCreate(CompanyDriveBase):
    pass

class CompanyDriveUpdate(BaseModel):
    company_name: Optional[str] = None
    role: Optional[str] = None
    tier: Optional[str] = None
    package_lpa: Optional[float] = None
    min_cgpa: Optional[float] = None
    min_tenth_percentage: Optional[float] = None
    min_twelfth_percentage: Optional[float] = None
    max_active_backlogs: Optional[int] = None
    max_history_backlogs: Optional[int] = None
    eligible_branches: Optional[str] = None
    required_skills: Optional[str] = None
    drive_date: Optional[str] = None
    registration_deadline: Optional[str] = None
    status: Optional[str] = None

class CompanyDriveResponse(CompanyDriveBase):
    id: int

    class Config:
        from_attributes = True

# --- Eligibility Filter & Evaluation Schemas ---
class EligibilityFilterRequest(BaseModel):
    company_id: Optional[int] = None
    min_cgpa: Optional[float] = None
    min_tenth_percentage: Optional[float] = None
    min_twelfth_percentage: Optional[float] = None
    max_active_backlogs: Optional[int] = None
    max_history_backlogs: Optional[int] = None
    eligible_branches: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    gender_filter: Optional[str] = "All" # All, Male, Female

class IneligibilityReason(BaseModel):
    criterion: str
    reason: str

class EvaluatedCandidate(BaseModel):
    student: StudentResponse
    is_eligible: bool
    reasons: List[str]
    readiness_score: float
    skill_match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]

class EligibilityResultResponse(BaseModel):
    total_students: int
    eligible_count: int
    ineligible_count: int
    eligibility_rate_percentage: float
    criteria_used: Dict[str, Any]
    candidates: List[EvaluatedCandidate]

# --- Skill Gap / Simulator Schemas ---
class SkillGapRequest(BaseModel):
    student_id: int
    company_id: int

class SkillGapResponse(BaseModel):
    student_name: str
    student_department: str
    company_name: str
    company_role: str
    is_eligible_academically: bool
    academic_reasons: List[str]
    match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]
    readiness_score: float

# --- Authentication Schemas ---
class StudentRegisterRequest(BaseModel):
    name: str
    roll_number: str
    email: str
    password: str
    department: str = "CSE"
    gender: Optional[str] = "Other"
    cgpa: float = Field(7.0, ge=0.0, le=10.0)
    tenth_percentage: float = Field(60.0, ge=0.0, le=100.0)
    twelfth_percentage: float = Field(60.0, ge=0.0, le=100.0)
    active_backlogs: int = Field(0, ge=0)
    history_of_backlogs: int = Field(0, ge=0)
    skills: Optional[str] = ""
    projects_count: Optional[int] = 0
    internships_count: Optional[int] = 0
    certifications_count: Optional[int] = 0

class LoginRequest(BaseModel):
    login_id: str # Can be email or roll number
    password: str
    role: Optional[str] = "student" # 'admin' or 'student'

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    student_id: Optional[int] = None
    roll_number: Optional[str] = None
    department: Optional[str] = None
    token: str

# --- Drive Application Schemas ---
class ApplicationCreate(BaseModel):
    student_id: int
    company_drive_id: int

class ApplicationResponse(BaseModel):
    id: int
    student_id: int
    company_drive_id: int
    company_name: str
    role: str
    package_lpa: float
    status: str
    applied_at: str

# --- What-If AI Simulator Schemas ---
class WhatIfRequest(BaseModel):
    student_id: int
    simulated_cgpa: Optional[float] = None
    simulated_active_backlogs: Optional[int] = None
    additional_skills: Optional[List[str]] = []
    additional_projects: Optional[int] = 0
    additional_internships: Optional[int] = 0

class WhatIfResponse(BaseModel):
    baseline_score: float
    simulated_score: float
    score_delta: float
    baseline_eligible_count: int
    simulated_eligible_count: int
    unlocked_companies: List[str]
    insights: List[str]

