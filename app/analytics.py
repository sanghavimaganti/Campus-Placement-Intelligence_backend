import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple

def calculate_readiness_score(student) -> float:
    """
    Computes an AI-weighted Placement Readiness Score (0-100) based on:
    - CGPA (35%)
    - School Academics (15%)
    - Active & History Backlogs penalty
    - Practical Experience: Internships (20%), Projects (15%), Certifications (15%)
    """
    cgpa = getattr(student, "cgpa", 0.0) or 0.0
    tenth = getattr(student, "tenth_percentage", 0.0) or 0.0
    twelfth = getattr(student, "twelfth_percentage", 0.0) or 0.0
    active_backlogs = getattr(student, "active_backlogs", 0) or 0
    history_backlogs = getattr(student, "history_of_backlogs", 0) or 0
    projects = getattr(student, "projects_count", 0) or 0
    internships = getattr(student, "internships_count", 0) or 0
    certifications = getattr(student, "certifications_count", 0) or 0

    # 1. CGPA component (Max 35)
    cgpa_score = (min(max(cgpa, 0.0), 10.0) / 10.0) * 35.0

    # 2. School Academics component (Max 15)
    school_avg = (tenth + twelfth) / 2.0
    school_score = (min(max(school_avg, 0.0), 100.0) / 100.0) * 15.0

    # 3. Practical projects (Max 15: 5 pts each, max 3)
    project_score = min(projects, 3) * 5.0

    # 4. Internships (Max 20: 10 pts each, max 2)
    internship_score = min(internships, 2) * 10.0

    # 5. Certifications (Max 15: 5 pts each, max 3)
    cert_score = min(certifications, 3) * 5.0

    total_score = cgpa_score + school_score + project_score + internship_score + cert_score

    # Penalties for backlogs
    penalty = (active_backlogs * 15.0) + (history_backlogs * 5.0)
    final_score = max(0.0, min(100.0, total_score - penalty))

    return round(final_score, 1)

def parse_skills_list(skills_str: str) -> List[str]:
    if not skills_str:
        return []
    return [s.strip().lower() for s in skills_str.split(",") if s.strip()]

def evaluate_student_eligibility(student, criteria: Dict[str, Any]) -> Tuple[bool, List[str], float, List[str], List[str]]:
    """
    Evaluates a single student against criteria dictionary:
    Returns (is_eligible, reasons, skill_match_percentage, matched_skills, missing_skills)
    """
    reasons = []
    min_cgpa = criteria.get("min_cgpa")
    min_tenth = criteria.get("min_tenth_percentage")
    min_twelfth = criteria.get("min_twelfth_percentage")
    max_active_backlogs = criteria.get("max_active_backlogs")
    max_history_backlogs = criteria.get("max_history_backlogs")
    eligible_branches = criteria.get("eligible_branches") or []
    required_skills = criteria.get("required_skills") or []
    gender_filter = criteria.get("gender_filter", "All")

    # CGPA Check
    if min_cgpa is not None and student.cgpa < min_cgpa:
        reasons.append(f"CGPA ({student.cgpa:.2f}) is below minimum requirement ({min_cgpa:.2f})")

    # 10th % Check
    if min_tenth is not None and student.tenth_percentage < min_tenth:
        reasons.append(f"10th Grade ({student.tenth_percentage:.1f}%) is below minimum requirement ({min_tenth:.1f}%)")

    # 12th % Check
    if min_twelfth is not None and student.twelfth_percentage < min_twelfth:
        reasons.append(f"12th Grade ({student.twelfth_percentage:.1f}%) is below minimum requirement ({min_twelfth:.1f}%)")

    # Active Backlogs Check
    if max_active_backlogs is not None and student.active_backlogs > max_active_backlogs:
        reasons.append(f"Active backlogs ({student.active_backlogs}) exceeds maximum allowed ({max_active_backlogs})")

    # History Backlogs Check
    if max_history_backlogs is not None and student.history_of_backlogs > max_history_backlogs:
        reasons.append(f"Historical backlogs ({student.history_of_backlogs}) exceeds maximum allowed ({max_history_backlogs})")

    # Branch Check
    if eligible_branches:
        branches_normalized = [b.strip().upper() for b in eligible_branches if b.strip()]
        if student.department.strip().upper() not in branches_normalized:
            reasons.append(f"Department '{student.department}' is not in eligible branches ({', '.join(branches_normalized)})")

    # Gender Check
    if gender_filter and gender_filter != "All":
        if student.gender.strip().lower() != gender_filter.strip().lower():
            reasons.append(f"Drive restricted to {gender_filter} candidates")

    # Skills Evaluation
    student_skills = parse_skills_list(student.skills)
    matched_skills = []
    missing_skills = []
    skill_match_percentage = 100.0

    if required_skills:
        req_clean = [s.strip().lower() for s in required_skills if s.strip()]
        if req_clean:
            for req in req_clean:
                # Substring or exact match
                if any(req in s or s in req for s in student_skills):
                    matched_skills.append(req.capitalize())
                else:
                    missing_skills.append(req.capitalize())
            
            match_ratio = len(matched_skills) / len(req_clean)
            skill_match_percentage = round(match_ratio * 100.0, 1)

            # If strict skill requirement, flag missing skills if match < 50%
            if match_ratio < 0.5:
                reasons.append(f"Skill match is only {skill_match_percentage}% (Missing: {', '.join(missing_skills)})")

    is_eligible = len(reasons) == 0
    return is_eligible, reasons, skill_match_percentage, matched_skills, missing_skills

def generate_analytics_summary(students: list, companies: list) -> Dict[str, Any]:
    """
    Computes high-level placement KPIs, distributions, and department breakdowns using Pandas.
    """
    if not students:
        return {
            "total_students": 0,
            "placed_students": 0,
            "unplaced_students": 0,
            "placement_rate": 0.0,
            "average_cgpa": 0.0,
            "average_readiness_score": 0.0,
            "department_stats": [],
            "cgpa_distribution": [],
            "backlog_distribution": [],
            "top_skills": [],
            "company_stats": {
                "total_companies": len(companies),
                "super_dream_count": sum(1 for c in companies if c.tier == "Super Dream"),
                "dream_count": sum(1 for c in companies if c.tier == "Dream"),
                "core_count": sum(1 for c in companies if c.tier not in ["Super Dream", "Dream"])
            }
        }

    # Convert student objects to dataframe for fast pandas operations
    data = []
    for s in students:
        readiness = calculate_readiness_score(s)
        data.append({
            "id": s.id,
            "roll_number": s.roll_number,
            "name": s.name,
            "gender": s.gender,
            "department": s.department.strip().upper(),
            "cgpa": float(s.cgpa),
            "tenth": float(s.tenth_percentage),
            "twelfth": float(s.twelfth_percentage),
            "active_backlogs": int(s.active_backlogs),
            "history_backlogs": int(s.history_of_backlogs),
            "placement_status": s.placement_status,
            "package_lpa": float(s.package_lpa) if s.package_lpa else 0.0,
            "readiness_score": readiness,
            "skills": s.skills or ""
        })

    df = pd.DataFrame(data)

    total_students = len(df)
    placed_mask = df["placement_status"].isin(["Placed", "Dream Placed"])
    placed_count = int(placed_mask.sum())
    unplaced_count = total_students - placed_count
    placement_rate = round((placed_count / total_students) * 100, 1) if total_students > 0 else 0.0
    avg_cgpa = round(float(df["cgpa"].mean()), 2)
    avg_readiness = round(float(df["readiness_score"].mean()), 1)
    
    # Placed average CTC
    placed_df = df[placed_mask]
    avg_ctc = round(float(placed_df["package_lpa"].mean()), 2) if not placed_df.empty and placed_df["package_lpa"].sum() > 0 else 0.0

    # Department breakdown
    dept_group = df.groupby("department")
    department_stats = []
    for dept, group in dept_group:
        dept_total = len(group)
        dept_placed = int(group["placement_status"].isin(["Placed", "Dream Placed"]).sum())
        department_stats.append({
            "department": str(dept),
            "total": dept_total,
            "placed": dept_placed,
            "unplaced": dept_total - dept_placed,
            "placement_rate": round((dept_placed / dept_total) * 100, 1) if dept_total > 0 else 0.0,
            "average_cgpa": round(float(group["cgpa"].mean()), 2),
            "average_readiness": round(float(group["readiness_score"].mean()), 1)
        })

    # CGPA Distribution
    bins = [0, 6.0, 7.0, 8.0, 9.0, 10.0]
    labels = ["< 6.0", "6.0 - 7.0", "7.0 - 8.0", "8.0 - 9.0", "9.0 - 10.0"]
    cgpa_binned = pd.cut(df["cgpa"], bins=bins, labels=labels, right=True)
    cgpa_counts = cgpa_binned.value_counts().sort_index()
    cgpa_distribution = [{"range": str(label), "count": int(cgpa_counts.get(label, 0))} for label in labels]

    # Backlogs Distribution
    backlog_counts = {
        "0 Backlogs": int((df["active_backlogs"] == 0).sum()),
        "1 Backlog": int((df["active_backlogs"] == 1).sum()),
        "2 Backlogs": int((df["active_backlogs"] == 2).sum()),
        "3+ Backlogs": int((df["active_backlogs"] >= 3).sum()),
    }
    backlog_distribution = [{"category": k, "count": v} for k, v in backlog_counts.items()]

    # Skill Frequency Distribution
    all_skills = []
    for s_str in df["skills"]:
        if s_str:
            tokens = [t.strip().title() for t in s_str.split(",") if t.strip()]
            all_skills.extend(tokens)
    
    top_skills = []
    if all_skills:
        skill_series = pd.Series(all_skills).value_counts().head(10)
        top_skills = [{"skill": k, "count": int(v)} for k, v in skill_series.items()]

    return {
        "total_students": total_students,
        "placed_students": placed_count,
        "unplaced_students": unplaced_count,
        "placement_rate": placement_rate,
        "average_cgpa": avg_cgpa,
        "average_ctc_lpa": avg_ctc,
        "average_readiness_score": avg_readiness,
        "department_stats": department_stats,
        "cgpa_distribution": cgpa_distribution,
        "backlog_distribution": backlog_distribution,
        "top_skills": top_skills,
        "company_stats": {
            "total_companies": len(companies),
            "super_dream_count": sum(1 for c in companies if c.tier == "Super Dream"),
            "dream_count": sum(1 for c in companies if c.tier == "Dream"),
            "core_count": sum(1 for c in companies if c.tier not in ["Super Dream", "Dream"])
        }
    }
