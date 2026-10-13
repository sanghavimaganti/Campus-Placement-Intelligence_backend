from sqlalchemy.orm import Session
from app.models import Student, CompanyDrive

INITIAL_COMPANIES = [
    {
        "company_name": "Google",
        "role": "Associate Software Engineer",
        "tier": "Super Dream",
        "package_lpa": 28.5,
        "min_cgpa": 8.5,
        "min_tenth_percentage": 75.0,
        "min_twelfth_percentage": 75.0,
        "max_active_backlogs": 0,
        "max_history_backlogs": 0,
        "eligible_branches": "CSE,IT,AIDS",
        "required_skills": "Python,Data Structures,Algorithms,Distributed Systems",
        "drive_date": "2026-11-15",
        "registration_deadline": "2026-11-05",
        "status": "Upcoming"
    },
    {
        "company_name": "Microsoft",
        "role": "Software Engineer (SDE 1)",
        "tier": "Super Dream",
        "package_lpa": 24.0,
        "min_cgpa": 8.0,
        "min_tenth_percentage": 70.0,
        "min_twelfth_percentage": 70.0,
        "max_active_backlogs": 0,
        "max_history_backlogs": 1,
        "eligible_branches": "CSE,IT,ECE,AIDS",
        "required_skills": "C++,Data Structures,Operating Systems,Cloud Computing",
        "drive_date": "2026-11-20",
        "registration_deadline": "2026-11-10",
        "status": "Upcoming"
    },
    {
        "company_name": "Amazon",
        "role": "Cloud Support Associate / SDE",
        "tier": "Super Dream",
        "package_lpa": 20.0,
        "min_cgpa": 7.8,
        "min_tenth_percentage": 70.0,
        "min_twelfth_percentage": 70.0,
        "max_active_backlogs": 0,
        "max_history_backlogs": 1,
        "eligible_branches": "CSE,IT,ECE,EEE",
        "required_skills": "Python,Linux,AWS,Networking",
        "drive_date": "2026-11-25",
        "registration_deadline": "2026-11-18",
        "status": "Upcoming"
    },
    {
        "company_name": "Qualcomm",
        "role": "Hardware & Firmware Engineer",
        "tier": "Super Dream",
        "package_lpa": 16.5,
        "min_cgpa": 7.5,
        "min_tenth_percentage": 65.0,
        "min_twelfth_percentage": 65.0,
        "max_active_backlogs": 0,
        "max_history_backlogs": 0,
        "eligible_branches": "ECE,EEE,CSE",
        "required_skills": "C,Embedded Systems,Verilog,Microcontrollers",
        "drive_date": "2026-12-02",
        "registration_deadline": "2026-11-26",
        "status": "Upcoming"
    },
    {
        "company_name": "Deloitte",
        "role": "Analyst - Technology Consulting",
        "tier": "Dream",
        "package_lpa": 10.5,
        "min_cgpa": 7.0,
        "min_tenth_percentage": 65.0,
        "min_twelfth_percentage": 65.0,
        "max_active_backlogs": 0,
        "max_history_backlogs": 1,
        "eligible_branches": "CSE,IT,ECE,EEE,MECH,AIDS",
        "required_skills": "SQL,Python,Power BI,Problem Solving",
        "drive_date": "2026-12-08",
        "registration_deadline": "2026-12-01",
        "status": "Upcoming"
    },
    {
        "company_name": "Cisco",
        "role": "Network Consulting Engineer",
        "tier": "Dream",
        "package_lpa": 13.0,
        "min_cgpa": 7.2,
        "min_tenth_percentage": 65.0,
        "min_twelfth_percentage": 65.0,
        "max_active_backlogs": 0,
        "max_history_backlogs": 1,
        "eligible_branches": "CSE,IT,ECE,EEE",
        "required_skills": "Networking,Python,Linux,CCNA",
        "drive_date": "2026-12-15",
        "registration_deadline": "2026-12-09",
        "status": "Upcoming"
    },
    {
        "company_name": "TCS Digital",
        "role": "Digital Technology Specialist",
        "tier": "Dream",
        "package_lpa": 7.5,
        "min_cgpa": 6.8,
        "min_tenth_percentage": 60.0,
        "min_twelfth_percentage": 60.0,
        "max_active_backlogs": 0,
        "max_history_backlogs": 2,
        "eligible_branches": "CSE,IT,ECE,EEE,MECH,AIDS",
        "required_skills": "Java,Python,SQL,Full Stack",
        "drive_date": "2026-12-20",
        "registration_deadline": "2026-12-14",
        "status": "Upcoming"
    },
    {
        "company_name": "Accenture",
        "role": "Advanced Associate Software Engineer",
        "tier": "Core/Regular",
        "package_lpa": 6.5,
        "min_cgpa": 6.5,
        "min_tenth_percentage": 60.0,
        "min_twelfth_percentage": 60.0,
        "max_active_backlogs": 1,
        "max_history_backlogs": 2,
        "eligible_branches": "CSE,IT,ECE,EEE,MECH,AIDS",
        "required_skills": "Java,JavaScript,SQL",
        "drive_date": "2026-12-28",
        "registration_deadline": "2026-12-22",
        "status": "Upcoming"
    },
    {
        "company_name": "Infosys",
        "role": "Systems Engineer Specialist",
        "tier": "Core/Regular",
        "package_lpa": 5.0,
        "min_cgpa": 6.0,
        "min_tenth_percentage": 60.0,
        "min_twelfth_percentage": 60.0,
        "max_active_backlogs": 1,
        "max_history_backlogs": 3,
        "eligible_branches": "CSE,IT,ECE,EEE,MECH,AIDS",
        "required_skills": "Python,Java,DBMS",
        "drive_date": "2027-01-05",
        "registration_deadline": "2026-12-30",
        "status": "Upcoming"
    }
]

STUDENT_TEMPLATES = [
    ("Aarav Sharma", "Male", "CSE", 9.4, 92.5, 90.0, 0, 0, "Python,Data Structures,Algorithms,Machine Learning,Docker", 3, 2, 2, "Dream Placed", "Google", 28.5),
    ("Ananya Iyer", "Female", "CSE", 9.1, 88.0, 89.5, 0, 0, "Python,SQL,React,Data Structures,AWS", 2, 2, 3, "Dream Placed", "Microsoft", 24.0),
    ("Rohan Verma", "Male", "IT", 8.7, 85.0, 86.0, 0, 0, "Java,Spring Boot,MySQL,React,Docker", 3, 1, 2, "Unplaced", None, None),
    ("Sneha Reddy", "Female", "AIDS", 8.9, 91.0, 88.0, 0, 0, "Python,TensorFlow,Machine Learning,SQL,Data Structures", 2, 1, 2, "Unplaced", None, None),
    ("Aditya Patel", "Male", "ECE", 8.2, 82.0, 84.0, 0, 0, "C,Embedded Systems,Verilog,Python,Microcontrollers", 2, 1, 1, "Unplaced", None, None),
    ("Pooja Nair", "Female", "ECE", 7.9, 84.0, 80.0, 0, 0, "C++,Networking,Python,Linux,CCNA", 2, 1, 1, "Unplaced", None, None),
    ("Vikram Singh", "Male", "EEE", 7.6, 78.0, 75.0, 0, 1, "MATLAB,Python,Power Systems,SQL", 1, 0, 1, "Unplaced", None, None),
    ("Divya Joshi", "Female", "CSE", 8.5, 87.0, 85.0, 0, 0, "Python,SQL,Power BI,Problem Solving,Data Structures", 2, 2, 2, "Placed", "Deloitte", 10.5),
    ("Karthik Raja", "Male", "MECH", 7.1, 74.0, 72.0, 1, 2, "AutoCAD,SolidWorks,Python,ANSYS", 1, 1, 0, "Unplaced", None, None),
    ("Meera Kulkarni", "Female", "IT", 8.3, 86.0, 82.0, 0, 0, "JavaScript,React,Node.js,MongoDB,Python", 3, 1, 2, "Placed", "TCS Digital", 7.5),
    ("Rahul Deshmukh", "Male", "CSE", 6.8, 70.0, 68.0, 1, 1, "Java,SQL,HTML,CSS", 1, 0, 1, "Unplaced", None, None),
    ("Kavya Pillai", "Female", "AIDS", 8.6, 89.0, 87.0, 0, 0, "Python,Deep Learning,NLP,SQL,Tableau", 2, 1, 2, "Unplaced", None, None),
    ("Harish Kumar", "Male", "ECE", 7.4, 76.0, 74.0, 0, 1, "C,Microcontrollers,Python,VLSI", 1, 0, 1, "Unplaced", None, None),
    ("Swati Saxena", "Female", "CSE", 7.8, 80.0, 79.0, 0, 0, "Java,Data Structures,SQL,SpringBoot", 2, 1, 1, "Placed", "TCS Digital", 7.5),
    ("Arjun Gupta", "Male", "IT", 6.4, 68.0, 65.0, 2, 3, "HTML,CSS,JavaScript,Basic Python", 1, 0, 0, "Unplaced", None, None),
    ("Neha Rao", "Female", "EEE", 8.1, 83.0, 81.0, 0, 0, "Python,IoT,C,Embedded Systems", 2, 1, 2, "Unplaced", None, None),
    ("Sanjay Menon", "Male", "MECH", 6.2, 65.0, 62.0, 0, 1, "CAD,Manufacturing,Quality Control", 1, 0, 0, "Unplaced", None, None),
    ("Priya Sen", "Female", "CSE", 8.8, 90.0, 88.0, 0, 0, "Python,AWS,Linux,Data Structures,Kubernetes", 3, 2, 2, "Unplaced", None, None),
    ("Gaurav Chauhan", "Male", "AIDS", 7.7, 79.0, 77.0, 0, 0, "Python,Pandas,SQL,Power BI,Machine Learning", 2, 1, 1, "Unplaced", None, None),
    ("Nandini Bhatt", "Female", "IT", 7.5, 78.0, 76.0, 0, 1, "Python,Java,SQL,DBMS", 1, 1, 1, "Placed", "Accenture", 6.5),
]

def seed_database_if_empty(db: Session):
    # Check if companies exist
    if db.query(CompanyDrive).count() == 0:
        for comp in INITIAL_COMPANIES:
            drive = CompanyDrive(**comp)
            db.add(drive)
        db.commit()

    # Check if students exist
    if db.query(Student).count() == 0:
        # Generate around 60 realistic students by repeating and varying names/departments
        roll_prefix_map = {
            "CSE": "21CS",
            "IT": "21IT",
            "ECE": "21EC",
            "EEE": "21EE",
            "MECH": "21ME",
            "AIDS": "21AD"
        }
        
        counter = {k: 1 for k in roll_prefix_map}
        students_to_add = []

        for i, (name, gender, dept, cgpa, tenth, twelfth, act_b, hist_b, skills, proj, intern, cert, status, company, lpa) in enumerate(STUDENT_TEMPLATES):
            roll = f"{roll_prefix_map.get(dept, '21ST')}{counter.get(dept, 1):03d}"
            counter[dept] = counter.get(dept, 1) + 1
            email = f"{name.lower().replace(' ', '.')}.{dept.lower()}@campus.edu"
            
            s = Student(
                roll_number=roll,
                name=name,
                email=email,
                gender=gender,
                department=dept,
                cgpa=cgpa,
                tenth_percentage=tenth,
                twelfth_percentage=twelfth,
                active_backlogs=act_b,
                history_of_backlogs=hist_b,
                skills=skills,
                projects_count=proj,
                internships_count=intern,
                certifications_count=cert,
                placement_status=status,
                placed_company=company,
                package_lpa=lpa
            )
            students_to_add.append(s)

        # Generate additional realistic records to reach 60+ candidates
        surnames = ["Kapoor", "Nath", "Choudhury", "Bose", "Das", "Murthy", "Natarajan", "Ghosh", "Pandey", "Saxena"]
        firstnames_m = ["Varun", "Abhinav", "Nikhil", "Siddharth", "Manish", "Kunal", "Tushar", "Rajesh", "Aakash", "Chetan"]
        firstnames_f = ["Rashi", "Isha", "Shruti", "Tanvi", "Bhavna", "Shalini", "Aditi", "Pallavi", "Kiran", "Geeta"]
        depts = ["CSE", "IT", "ECE", "EEE", "MECH", "AIDS"]

        for idx in range(35):
            is_female = idx % 2 == 1
            name = f"{firstnames_f[idx % len(firstnames_f)] if is_female else firstnames_m[idx % len(firstnames_m)]} {surnames[idx % len(surnames)]}"
            dept = depts[idx % len(depts)]
            roll = f"{roll_prefix_map.get(dept, '21ST')}{counter.get(dept, 1):03d}"
            counter[dept] = counter.get(dept, 1) + 1
            email = f"{name.lower().replace(' ', '.')}.{idx+20}@campus.edu"
            
            cgpa = round(6.0 + (idx * 0.11) % 3.9, 2)
            tenth = round(65.0 + (idx * 0.9) % 30.0, 1)
            twelfth = round(62.0 + (idx * 0.85) % 32.0, 1)
            act_b = 1 if (idx % 7 == 0) else (2 if idx % 19 == 0 else 0)
            hist_b = act_b + (1 if idx % 5 == 0 else 0)
            proj = (idx % 4)
            intern = 1 if (idx % 3 == 0) else 0
            cert = (idx % 3)
            skills = "Python,SQL,Data Structures,Web Development" if dept in ["CSE", "IT", "AIDS"] else "C,Embedded Systems,MATLAB,Python"

            s = Student(
                roll_number=roll,
                name=name,
                email=email,
                gender="Female" if is_female else "Male",
                department=dept,
                cgpa=cgpa,
                tenth_percentage=tenth,
                twelfth_percentage=twelfth,
                active_backlogs=act_b,
                history_of_backlogs=hist_b,
                skills=skills,
                projects_count=proj,
                internships_count=intern,
                certifications_count=cert,
                placement_status="Unplaced",
                placed_company=None,
                package_lpa=None
            )
            students_to_add.append(s)

        db.bulk_save_objects(students_to_add)
        db.commit()
