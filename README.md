# Campus Placement Intelligence & Eligibility Dashboard - Backend

High-performance REST API built with **FastAPI**, **Pandas**, and **SQLAlchemy** for automated student campus placement screening, predictive readiness scoring, company criteria matching, and real-time analytics.

---

## Key Features

- **Multi-Criteria Eligibility Filter Engine**:
  - Filter students dynamically by CGPA, 10th & 12th marks, active backlogs, historical backlogs, branches, required skills, and gender.
  - Detailed diagnostic feedback: Explains exactly why a student was disqualified.
- **AI Placement Readiness Score (0-100)**:
  - Multi-factor evaluation across academics, backlogs, technical projects, internships, and certifications.
- **Skill Gap & Simulator Analysis**:
  - Compares student skills against target company requirements with actionable recommendations.
- **Real-Time Analytics & KPIs**:
  - Department-wise placement and eligibility breakdown.
  - CGPA bracket distributions & backlogs charts.
  - Top in-demand campus skills aggregation.
- **One-Click Export**:
  - Export filtered lists directly to styled **Excel (.xlsx)** and **CSV**.
- **Bulk Student Upload**:
  - Upload entire student cohorts via CSV or Excel with instant validation and DB sync.
- **Dual Database Support**:
  - Zero-config portable **SQLite** out-of-the-box.
  - Production **MySQL** and **PostgreSQL** support via `DATABASE_URL`.

---

## Local Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run API Server
```bash
uvicorn main:app --reload --port 8000
```

The interactive Swagger API documentation will be available at:
`http://localhost:8000/docs`

---

## Deploying to Render

1. Create a new **Web Service** on [Render](https://render.com).
2. Connect this repository: `https://github.com/sanghavimaganti/Campus-Placement-Intelligence_backend.git`.
3. Set the following settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. (Optional) Set `DATABASE_URL` environment variable if connecting to an external MySQL or PostgreSQL database.
5. Click **Deploy Web Service**.
