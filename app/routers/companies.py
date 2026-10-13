from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CompanyDrive
from app.schemas import CompanyDriveCreate, CompanyDriveUpdate, CompanyDriveResponse

router = APIRouter(prefix="/companies", tags=["Company Drives"])

@router.get("", response_model=List[CompanyDriveResponse])
def get_companies(
    status: Optional[str] = Query(None, description="Filter by status (Upcoming, Ongoing, Completed)"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    db: Session = Depends(get_db)
):
    query = db.query(CompanyDrive)
    if status and status != "All":
        query = query.filter(CompanyDrive.status == status)
    if tier and tier != "All":
        query = query.filter(CompanyDrive.tier == tier)

    return query.order_by(CompanyDrive.package_lpa.desc()).all()

@router.get("/{company_id}", response_model=CompanyDriveResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    drive = db.query(CompanyDrive).filter(CompanyDrive.id == company_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Company drive not found")
    return drive

@router.post("", response_model=CompanyDriveResponse, status_code=201)
def create_company_drive(drive_in: CompanyDriveCreate, db: Session = Depends(get_db)):
    new_drive = CompanyDrive(**drive_in.dict())
    db.add(new_drive)
    db.commit()
    db.refresh(new_drive)
    return new_drive

@router.put("/{company_id}", response_model=CompanyDriveResponse)
def update_company_drive(company_id: int, drive_in: CompanyDriveUpdate, db: Session = Depends(get_db)):
    drive = db.query(CompanyDrive).filter(CompanyDrive.id == company_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Company drive not found")

    update_data = drive_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(drive, field, value)

    db.commit()
    db.refresh(drive)
    return drive

@router.delete("/{company_id}")
def delete_company_drive(company_id: int, db: Session = Depends(get_db)):
    drive = db.query(CompanyDrive).filter(CompanyDrive.id == company_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Company drive not found")
    db.delete(drive)
    db.commit()
    return {"message": f"Company drive '{drive.company_name} - {drive.role}' deleted successfully"}
