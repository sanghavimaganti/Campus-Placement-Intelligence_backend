import io
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, CompanyDrive
from app.schemas import (
    EligibilityFilterRequest,
    EligibilityResultResponse,
    EvaluatedCandidate,
    StudentResponse,
    SkillGapRequest,
    SkillGapResponse
)
from app.analytics import (
    calculate_readiness_score,
    evaluate_student_eligibility,
    parse_skills_list
)

router = APIRouter(prefix="/eligibility", tags=["Eligibility Engine"])

def _resolve_criteria(request: EligibilityFilterRequest, db: Session) -> Dict[str, Any]:
    criteria = {
        "min_cgpa": request.min_cgpa if request.min_cgpa is not None else 0.0,
        "min_tenth_percentage": request.min_tenth_percentage if request.min_tenth_percentage is not None else 0.0,
        "min_twelfth_percentage": request.min_twelfth_percentage if request.min_twelfth_percentage is not None else 0.0,
        "max_active_backlogs": request.max_active_backlogs if request.max_active_backlogs is not None else 10,
        "max_history_backlogs": request.max_history_backlogs if request.max_history_backlogs is not None else 10,
        "eligible_branches": request.eligible_branches or [],
        "required_skills": request.required_skills or [],
        "gender_filter": request.gender_filter or "All",
        "company_name": "Custom Filter"
    }

    if request.company_id:
        company = db.query(CompanyDrive).filter(CompanyDrive.id == request.company_id).first()
        if company:
            criteria["company_name"] = company.company_name
            criteria["role"] = company.role
            criteria["package_lpa"] = company.package_lpa
            if request.min_cgpa is None:
                criteria["min_cgpa"] = company.min_cgpa
            if request.min_tenth_percentage is None:
                criteria["min_tenth_percentage"] = company.min_tenth_percentage
            if request.min_twelfth_percentage is None:
                criteria["min_twelfth_percentage"] = company.min_twelfth_percentage
            if request.max_active_backlogs is None:
                criteria["max_active_backlogs"] = company.max_active_backlogs
            if request.max_history_backlogs is None:
                criteria["max_history_backlogs"] = company.max_history_backlogs
            if not request.eligible_branches and company.eligible_branches:
                criteria["eligible_branches"] = [b.strip() for b in company.eligible_branches.split(",") if b.strip()]
            if not request.required_skills and company.required_skills:
                criteria["required_skills"] = [s.strip() for s in company.required_skills.split(",") if s.strip()]

    return criteria

@router.post("/evaluate", response_model=EligibilityResultResponse)
def evaluate_eligibility(request: EligibilityFilterRequest, db: Session = Depends(get_db)):
    criteria = _resolve_criteria(request, db)
    students = db.query(Student).all()

    evaluated_candidates = []
    eligible_count = 0

    for s in students:
        readiness = calculate_readiness_score(s)
        is_elig, reasons, match_pct, matched, missing = evaluate_student_eligibility(s, criteria)
        
        if is_elig:
            eligible_count += 1

        s_dict = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        s_dict["readiness_score"] = readiness

        evaluated_candidates.append(
            EvaluatedCandidate(
                student=StudentResponse(**s_dict),
                is_eligible=is_elig,
                reasons=reasons,
                readiness_score=readiness,
                skill_match_percentage=match_pct,
                matched_skills=matched,
                missing_skills=missing
            )
        )

    # Sort: Eligible students first (by CGPA desc), then ineligible (by CGPA desc)
    evaluated_candidates.sort(key=lambda c: (1 if c.is_eligible else 0, c.student.cgpa), reverse=True)

    total = len(students)
    rate = round((eligible_count / total * 100.0), 1) if total > 0 else 0.0

    return EligibilityResultResponse(
        total_students=total,
        eligible_count=eligible_count,
        ineligible_count=total - eligible_count,
        eligibility_rate_percentage=rate,
        criteria_used=criteria,
        candidates=evaluated_candidates
    )

@router.post("/skill-gap", response_model=SkillGapResponse)
def check_skill_gap(request: SkillGapRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    company = db.query(CompanyDrive).filter(CompanyDrive.id == request.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company drive not found")

    criteria = {
        "min_cgpa": company.min_cgpa,
        "min_tenth_percentage": company.min_tenth_percentage,
        "min_twelfth_percentage": company.min_twelfth_percentage,
        "max_active_backlogs": company.max_active_backlogs,
        "max_history_backlogs": company.max_history_backlogs,
        "eligible_branches": [b.strip() for b in company.eligible_branches.split(",") if b.strip()],
        "required_skills": [s.strip() for s in company.required_skills.split(",") if s.strip()]
    }

    is_acad_elig, acad_reasons, match_pct, matched_skills, missing_skills = evaluate_student_eligibility(student, criteria)
    readiness = calculate_readiness_score(student)

    # Generate actionable recommendations
    recommendations = []
    if missing_skills:
        recommendations.append(f"Focus on mastering the required skills: {', '.join(missing_skills)} through hands-on projects.")
    if student.active_backlogs > 0:
        recommendations.append(f"Clear active backlogs immediately as {company.company_name} requires 0 active backlogs.")
    if student.cgpa < company.min_cgpa:
        recommendations.append(f"Target semester exams to raise CGPA above {company.min_cgpa:.2f} (Current: {student.cgpa:.2f}).")
    if student.projects_count < 2:
        recommendations.append(f"Build at least 2 real-world portfolio projects aligning with {company.role}.")
    if student.internships_count == 0:
        recommendations.append("Pursue industrial internships or open-source contributions to boost profile.")
    if not recommendations:
        recommendations.append("Candidate strongly meets all academic and skill requirements. Ready for mock interviews!")

    return SkillGapResponse(
        student_name=student.name,
        student_department=student.department,
        company_name=company.company_name,
        company_role=company.role,
        is_eligible_academically=is_acad_elig,
        academic_reasons=acad_reasons,
        match_percentage=match_pct,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        recommendations=recommendations,
        readiness_score=readiness
    )

@router.post("/export-csv")
def export_eligible_csv(
    request: EligibilityFilterRequest,
    only_eligible: bool = Query(True, description="Export only eligible students if true, or all if false"),
    db: Session = Depends(get_db)
):
    criteria = _resolve_criteria(request, db)
    students = db.query(Student).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Roll Number", "Name", "Department", "Gender", "CGPA",
        "10th %", "12th %", "Active Backlogs", "Skills",
        "Eligibility Status", "Disqualification Reasons", "Readiness Score", "Skill Match %"
    ])

    for s in students:
        readiness = calculate_readiness_score(s)
        is_elig, reasons, match_pct, matched, missing = evaluate_student_eligibility(s, criteria)

        if only_eligible and not is_elig:
            continue

        writer.writerow([
            s.roll_number,
            s.name,
            s.department,
            s.gender,
            s.cgpa,
            s.tenth_percentage,
            s.twelfth_percentage,
            s.active_backlogs,
            s.skills,
            "ELIGIBLE" if is_elig else "INELIGIBLE",
            "; ".join(reasons) if reasons else "None",
            readiness,
            f"{match_pct}%"
        ])

    csv_data = output.getvalue().encode("utf-8")
    filename = f"eligible_students_{criteria.get('company_name', 'drive').replace(' ', '_')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/export-excel")
def export_eligible_excel(
    request: EligibilityFilterRequest,
    only_eligible: bool = Query(True),
    db: Session = Depends(get_db)
):
    criteria = _resolve_criteria(request, db)
    students = db.query(Student).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Eligible Candidates"

    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    align_center = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    headers = [
        "Roll Number", "Name", "Department", "Gender", "CGPA",
        "10th %", "12th %", "Active Backlogs", "Skills",
        "Eligibility Status", "Disqualification Reasons", "Readiness Score", "Skill Match %"
    ]

    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center

    eligible_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    ineligible_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

    row_idx = 2
    for s in students:
        readiness = calculate_readiness_score(s)
        is_elig, reasons, match_pct, matched, missing = evaluate_student_eligibility(s, criteria)

        if only_eligible and not is_elig:
            continue

        row_data = [
            s.roll_number,
            s.name,
            s.department,
            s.gender,
            s.cgpa,
            s.tenth_percentage,
            s.twelfth_percentage,
            s.active_backlogs,
            s.skills,
            "ELIGIBLE" if is_elig else "INELIGIBLE",
            "; ".join(reasons) if reasons else "None",
            readiness,
            f"{match_pct}%"
        ]
        ws.append(row_data)

        status_cell = ws.cell(row=row_idx, column=10)
        status_cell.fill = eligible_fill if is_elig else ineligible_fill
        status_cell.font = Font(bold=True, color="166534" if is_elig else "991B1B")

        for c_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=c_idx)
            cell.border = thin_border
            if c_idx not in [2, 9, 11]:
                cell.alignment = align_center

        row_idx += 1

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    filename = f"eligible_candidates_{criteria.get('company_name', 'drive').replace(' ', '_')}.xlsx"
    return Response(
        content=excel_file.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
