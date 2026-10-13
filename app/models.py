import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    gender = Column(String(20), default="Other")
    department = Column(String(50), index=True, nullable=False) # e.g. CSE, IT, ECE, EEE, MECH, AIDS
    cgpa = Column(Float, index=True, nullable=False)
    tenth_percentage = Column(Float, nullable=False)
    twelfth_percentage = Column(Float, nullable=False)
    active_backlogs = Column(Integer, default=0, nullable=False)
    history_of_backlogs = Column(Integer, default=0, nullable=False)
    skills = Column(Text, default="") # Comma-separated
    projects_count = Column(Integer, default=0)
    internships_count = Column(Integer, default=0)
    certifications_count = Column(Integer, default=0)
    placement_status = Column(String(50), default="Unplaced") # Unplaced, Placed, Dream Placed
    placed_company = Column(String(100), nullable=True)
    package_lpa = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CompanyDrive(Base):
    __tablename__ = "company_drives"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(100), index=True, nullable=False)
    role = Column(String(100), nullable=False)
    tier = Column(String(50), default="Dream") # Super Dream, Dream, Core/Regular
    package_lpa = Column(Float, nullable=False)
    min_cgpa = Column(Float, default=7.0, nullable=False)
    min_tenth_percentage = Column(Float, default=60.0, nullable=False)
    min_twelfth_percentage = Column(Float, default=60.0, nullable=False)
    max_active_backlogs = Column(Integer, default=0, nullable=False)
    max_history_backlogs = Column(Integer, default=1, nullable=False)
    eligible_branches = Column(String(255), default="CSE,IT,ECE") # Comma-separated
    required_skills = Column(String(255), default="Python,SQL") # Comma-separated
    drive_date = Column(String(50), default="")
    registration_deadline = Column(String(50), default="")
    status = Column(String(50), default="Upcoming") # Upcoming, Ongoing, Completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), default="student", nullable=False) # 'admin' or 'student'
    password_hash = Column(String(255), nullable=False)
    student_id = Column(Integer, nullable=True) # Linked Student id if role is student
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DriveApplication(Base):
    __tablename__ = "drive_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, index=True, nullable=False)
    company_drive_id = Column(Integer, index=True, nullable=False)
    status = Column(String(50), default="Applied") # 'Applied', 'Shortlisted', 'Interview Scheduled', 'Selected'
    applied_at = Column(DateTime, default=datetime.datetime.utcnow)
