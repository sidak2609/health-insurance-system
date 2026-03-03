import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import json
from datetime import datetime, timedelta

from app.db.database import create_tables, SessionLocal
from app.db.models import Policy, User, Claim, Notification, AuditLog
from app.api.routes import auth, eligibility, claims, policies, dashboard, premium, documents, notifications


def _seed_demo_users(db):
    from app.services.auth_service import hash_password

    demo_emails = [
        "rajesh@patient.com", "priya@patient.com", "arjun@patient.com",
        "meera@patient.com", "vikram@patient.com", "ananya@patient.com",
        "suresh@patient.com", "kavya@patient.com", "rohit@patient.com",
        "deepa@patient.com", "anil@patient.com", "sunita@patient.com",
        "kiran@patient.com", "pooja@patient.com", "ramesh@patient.com",
        "nisha@patient.com", "sanjay@patient.com", "admin@insurer.com",
    ]
    existing_emails = {u.email for u in db.query(User).all()}
    if all(e in existing_emails for e in demo_emails):
        return

    demo_users = [
        User(email="rajesh@patient.com", hashed_password=hash_password("password123"),
             full_name="Rajesh Kumar", role="patient", age=35, bmi=26.2, is_smoker=False,
             pre_existing_conditions=json.dumps(["diabetes", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=120)),
        User(email="priya@patient.com", hashed_password=hash_password("password123"),
             full_name="Priya Sharma", role="patient", age=28, bmi=22.1, is_smoker=True,
             pre_existing_conditions=json.dumps(["asthma"]),
             created_at=datetime.utcnow() - timedelta(days=90)),
        User(email="arjun@patient.com", hashed_password=hash_password("password123"),
             full_name="Arjun Mehta", role="patient", age=52, bmi=31.5, is_smoker=True,
             pre_existing_conditions=json.dumps(["diabetes", "heart_disease", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=180)),
        User(email="meera@patient.com", hashed_password=hash_password("password123"),
             full_name="Meera Nair", role="patient", age=31, bmi=23.8, is_smoker=False,
             pre_existing_conditions=json.dumps(["thyroid"]),
             created_at=datetime.utcnow() - timedelta(days=60)),
        User(email="vikram@patient.com", hashed_password=hash_password("password123"),
             full_name="Vikram Singh", role="patient", age=45, bmi=28.4, is_smoker=False,
             pre_existing_conditions=json.dumps(["back_pain", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=75)),
        User(email="ananya@patient.com", hashed_password=hash_password("password123"),
             full_name="Ananya Reddy", role="patient", age=26, bmi=20.5, is_smoker=False,
             pre_existing_conditions=json.dumps([]),
             created_at=datetime.utcnow() - timedelta(days=30)),
        User(email="suresh@patient.com", hashed_password=hash_password("password123"),
             full_name="Suresh Pillai", role="patient", age=62, bmi=27.9, is_smoker=False,
             pre_existing_conditions=json.dumps(["arthritis", "diabetes"]),
             created_at=datetime.utcnow() - timedelta(days=200)),
        User(email="kavya@patient.com", hashed_password=hash_password("password123"),
             full_name="Kavya Iyer", role="patient", age=24, bmi=21.0, is_smoker=False,
             pre_existing_conditions=json.dumps([]),
             created_at=datetime.utcnow() - timedelta(days=15)),
        User(email="rohit@patient.com", hashed_password=hash_password("password123"),
             full_name="Rohit Gupta", role="patient", age=58, bmi=29.5, is_smoker=False,
             pre_existing_conditions=json.dumps(["heart_disease", "high_cholesterol"]),
             created_at=datetime.utcnow() - timedelta(days=150)),
        User(email="deepa@patient.com", hashed_password=hash_password("password123"),
             full_name="Deepa Krishnan", role="patient", age=33, bmi=24.5, is_smoker=False,
             pre_existing_conditions=json.dumps(["PCOS", "thyroid"]),
             created_at=datetime.utcnow() - timedelta(days=45)),
        User(email="anil@patient.com", hashed_password=hash_password("password123"),
             full_name="Anil Bhat", role="patient", age=67, bmi=26.1, is_smoker=False,
             pre_existing_conditions=json.dumps(["arthritis", "cataract", "diabetes"]),
             created_at=datetime.utcnow() - timedelta(days=240)),
        User(email="sunita@patient.com", hashed_password=hash_password("password123"),
             full_name="Sunita Verma", role="patient", age=42, bmi=22.8, is_smoker=False,
             pre_existing_conditions=json.dumps(["breast_cancer_remission"]),
             created_at=datetime.utcnow() - timedelta(days=100)),
        User(email="kiran@patient.com", hashed_password=hash_password("password123"),
             full_name="Kiran Rao", role="patient", age=38, bmi=23.1, is_smoker=True,
             pre_existing_conditions=json.dumps(["kidney_disease"]),
             created_at=datetime.utcnow() - timedelta(days=130)),
        User(email="pooja@patient.com", hashed_password=hash_password("password123"),
             full_name="Pooja Joshi", role="patient", age=29, bmi=19.8, is_smoker=False,
             pre_existing_conditions=json.dumps(["depression", "anxiety"]),
             created_at=datetime.utcnow() - timedelta(days=55)),
        User(email="ramesh@patient.com", hashed_password=hash_password("password123"),
             full_name="Ramesh Chauhan", role="patient", age=55, bmi=30.2, is_smoker=True,
             pre_existing_conditions=json.dumps(["COPD", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=160)),
        User(email="nisha@patient.com", hashed_password=hash_password("password123"),
             full_name="Nisha Agarwal", role="patient", age=29, bmi=24.0, is_smoker=False,
             pre_existing_conditions=json.dumps(["anemia"]),
             created_at=datetime.utcnow() - timedelta(days=20)),
        User(email="sanjay@patient.com", hashed_password=hash_password("password123"),
             full_name="Sanjay Malhotra", role="patient", age=48, bmi=35.2, is_smoker=False,
             pre_existing_conditions=json.dumps(["hypertension", "obesity", "sleep_apnea"]),
             created_at=datetime.utcnow() - timedelta(days=110)),
        User(email="admin@insurer.com", hashed_password=hash_password("password123"),
             full_name="Dr. Amit Patel", role="insurer", company_name="Star Health Insurance",
             created_at=datetime.utcnow() - timedelta(days=365)),
    ]

    added = 0
    for u in demo_users:
        if u.email not in existing_emails:
            db.add(u)
            added += 1
    db.commit()
    print(f"Demo users seeded: {added} new users added.")


def _seed_demo_claims(db):
    from app.services.risk_scoring import calculate_risk_score

    users = {u.email: u for u in db.query(User).all()}
    policies_map = {p.name: p for p in db.query(Policy).all()}
    insurer = users.get("admin@insurer.com")

    # Only seed claims for patients who have none yet
    patient_ids_with_claims = {
        row[0] for row in db.query(Claim.patient_id).distinct().all()
    }
    patients_needing_claims = {
        email: u for email, u in users.items()
        if u.role == "patient" and u.id not in patient_ids_with_claims
    }
    if not patients_needing_claims:
        return

    if not insurer or not policies_map:
        print("Skipping claims seed: users or policies not ready.")
        return

    basic = policies_map.get("Basic Health Plan")
    standard = policies_map.get("Standard Health Plan")
    premium = policies_map.get("Premium Health Plan")
    senior = policies_map.get("Senior Care Plan")
    maternity = policies_map.get("Maternity Plus Plan")
    critical = policies_map.get("Critical Illness Shield")
    family = policies_map.get("Family Floater Plan")

    # Fallback: use any available policy
    fallback = basic or standard or premium or next(iter(policies_map.values()), None)

    def p(name):
        return policies_map.get(name) or fallback

    raw_claims = [
        # ── Rajesh Kumar (diabetes + hypertension, Standard plan) ──
        dict(email="rajesh@patient.com", policy="Standard Health Plan",
             claim_type="hospitalization", amount_claimed=37500.0, status="approved",
             amount_approved=35000.0, reviewer=insurer.id,
             description="Emergency admission for chest pain. ECG and troponin done. Overnight observation at Apollo Hospital.",
             days_ago=110),
        dict(email="rajesh@patient.com", policy="Standard Health Plan",
             claim_type="prescription", amount_claimed=2500.0, status="approved",
             amount_approved=2500.0, reviewer=insurer.id,
             description="Monthly diabetes medication: Metformin 500mg and insulin glargine from MedPlus.",
             days_ago=90),
        dict(email="rajesh@patient.com", policy="Standard Health Plan",
             claim_type="outpatient", amount_claimed=3000.0, status="pending",
             description="Specialist consultation for HbA1c review and diabetes management at Fortis.",
             days_ago=5),
        dict(email="rajesh@patient.com", policy="Standard Health Plan",
             claim_type="dental", amount_claimed=5000.0, status="rejected",
             reviewer=insurer.id,
             description="Dental cleaning and cavity filling at Clove Dental.",
             rejection_reason="Dental services not covered under Standard Health Plan.",
             days_ago=50),
        dict(email="rajesh@patient.com", policy="Standard Health Plan",
             claim_type="laboratory", amount_claimed=1800.0, status="approved",
             amount_approved=1800.0, reviewer=insurer.id,
             description="Quarterly blood panel: HbA1c, lipid profile, kidney function tests.",
             days_ago=70),
        dict(email="rajesh@patient.com", policy="Standard Health Plan",
             claim_type="prescription", amount_claimed=3200.0, status="approved",
             amount_approved=3200.0, reviewer=insurer.id,
             description="Amlodipine 5mg and Telmisartan 40mg for hypertension — 3-month supply.",
             days_ago=30),

        # ── Priya Sharma (asthma, smoker, Basic plan) ──
        dict(email="priya@patient.com", policy="Basic Health Plan",
             claim_type="outpatient", amount_claimed=1800.0, status="approved",
             amount_approved=1800.0, reviewer=insurer.id,
             description="Asthma follow-up and spirometry at Max Hospital.",
             days_ago=80),
        dict(email="priya@patient.com", policy="Basic Health Plan",
             claim_type="prescription", amount_claimed=1200.0, status="approved",
             amount_approved=1200.0, reviewer=insurer.id,
             description="Asthalin inhaler and Montelukast refill from Netmeds.",
             days_ago=60),
        dict(email="priya@patient.com", policy="Premium Health Plan",
             claim_type="hospitalization", amount_claimed=100000.0, status="under_review",
             description="Severe asthma attack — 3-day ICU stay at AIIMS with nebulization.",
             days_ago=3),
        dict(email="priya@patient.com", policy="Basic Health Plan",
             claim_type="vision", amount_claimed=3200.0, status="rejected",
             reviewer=insurer.id,
             description="Annual eye exam and prescription glasses from Lenskart.",
             rejection_reason="Vision care excluded from Basic Health Plan.",
             days_ago=40),
        dict(email="priya@patient.com", policy="Basic Health Plan",
             claim_type="emergency", amount_claimed=8500.0, status="approved",
             amount_approved=8500.0, reviewer=insurer.id,
             description="Emergency bronchodilator treatment at Apollo ER — 4-hour observation.",
             days_ago=20),

        # ── Arjun Mehta (diabetes + heart + hypertension, smoker) ──
        dict(email="arjun@patient.com", policy="Premium Health Plan",
             claim_type="hospitalization", amount_claimed=250000.0, status="approved",
             amount_approved=230000.0, reviewer=insurer.id,
             description="CABG (triple bypass surgery) at Narayana Health. 8-day ICU + ward stay.",
             days_ago=160),
        dict(email="arjun@patient.com", policy="Premium Health Plan",
             claim_type="prescription", amount_claimed=8500.0, status="approved",
             amount_approved=8500.0, reviewer=insurer.id,
             description="Post-cardiac medications: Clopidogrel, Atorvastatin, Metoprolol, Ramipril.",
             days_ago=140),
        dict(email="arjun@patient.com", policy="Premium Health Plan",
             claim_type="outpatient", amount_claimed=5000.0, status="approved",
             amount_approved=5000.0, reviewer=insurer.id,
             description="Cardiologist follow-up: stress ECG and echocardiogram.",
             days_ago=120),
        dict(email="arjun@patient.com", policy="Premium Health Plan",
             claim_type="laboratory", amount_claimed=4200.0, status="approved",
             amount_approved=4200.0, reviewer=insurer.id,
             description="Cardiac enzymes, HbA1c, kidney function, lipid profile.",
             days_ago=100),
        dict(email="arjun@patient.com", policy="Premium Health Plan",
             claim_type="hospitalization", amount_claimed=45000.0, status="pending",
             description="Hypoglycemia episode — overnight observation at Fortis Hospital.",
             days_ago=10),

        # ── Meera Nair (thyroid) ──
        dict(email="meera@patient.com", policy="Standard Health Plan",
             claim_type="prescription", amount_claimed=800.0, status="approved",
             amount_approved=800.0, reviewer=insurer.id,
             description="Levothyroxine 50mcg — 3-month supply from Apollo Pharmacy.",
             days_ago=55),
        dict(email="meera@patient.com", policy="Standard Health Plan",
             claim_type="laboratory", amount_claimed=1200.0, status="approved",
             amount_approved=1200.0, reviewer=insurer.id,
             description="Thyroid panel: TSH, T3, T4, Anti-TPO antibodies.",
             days_ago=50),
        dict(email="meera@patient.com", policy="Standard Health Plan",
             claim_type="outpatient", amount_claimed=2200.0, status="approved",
             amount_approved=2200.0, reviewer=insurer.id,
             description="Endocrinologist consultation for thyroid dose adjustment.",
             days_ago=45),
        dict(email="meera@patient.com", policy="Standard Health Plan",
             claim_type="maternity", amount_claimed=55000.0, status="approved",
             amount_approved=50000.0, reviewer=insurer.id,
             description="Normal delivery at Cloudnine Hospital — 2-day stay.",
             days_ago=15),

        # ── Vikram Singh (back pain + hypertension) ──
        dict(email="vikram@patient.com", policy="Standard Health Plan",
             claim_type="outpatient", amount_claimed=2500.0, status="approved",
             amount_approved=2500.0, reviewer=insurer.id,
             description="Orthopaedic consultation and MRI of lumbar spine at Manipal Hospital.",
             days_ago=70),
        dict(email="vikram@patient.com", policy="Standard Health Plan",
             claim_type="physiotherapy", amount_claimed=9600.0, status="approved",
             amount_approved=9600.0, reviewer=insurer.id,
             description="12 physiotherapy sessions for L4-L5 disc herniation at Apollo PT centre.",
             days_ago=50),
        dict(email="vikram@patient.com", policy="Standard Health Plan",
             claim_type="prescription", amount_claimed=1500.0, status="approved",
             amount_approved=1500.0, reviewer=insurer.id,
             description="Amlodipine, Etoricoxib, and muscle relaxants — 2-month supply.",
             days_ago=30),
        dict(email="vikram@patient.com", policy="Standard Health Plan",
             claim_type="hospitalization", amount_claimed=75000.0, status="pending",
             description="Minimally invasive spinal decompression surgery (MISS) at Fortis.",
             days_ago=4),

        # ── Ananya Reddy (no pre-existing, young and healthy) ──
        dict(email="ananya@patient.com", policy="Basic Health Plan",
             claim_type="emergency", amount_claimed=12000.0, status="approved",
             amount_approved=12000.0, reviewer=insurer.id,
             description="Food poisoning — IV fluids and anti-emetics at ER. 6-hour observation.",
             days_ago=25),
        dict(email="ananya@patient.com", policy="Basic Health Plan",
             claim_type="outpatient", amount_claimed=900.0, status="approved",
             amount_approved=900.0, reviewer=insurer.id,
             description="Primary care visit for fever and sore throat.",
             days_ago=10),

        # ── Suresh Pillai (arthritis + diabetes, elderly) ──
        dict(email="suresh@patient.com", policy="Senior Care Plan",
             claim_type="hospitalization", amount_claimed=180000.0, status="approved",
             amount_approved=170000.0, reviewer=insurer.id,
             description="Right knee total replacement (TKR) at KIMS Hospital — 5-day stay.",
             days_ago=180),
        dict(email="suresh@patient.com", policy="Senior Care Plan",
             claim_type="physiotherapy", amount_claimed=24000.0, status="approved",
             amount_approved=24000.0, reviewer=insurer.id,
             description="Post-TKR physiotherapy — 30 sessions over 10 weeks.",
             days_ago=130),
        dict(email="suresh@patient.com", policy="Senior Care Plan",
             claim_type="prescription", amount_claimed=6500.0, status="approved",
             amount_approved=6500.0, reviewer=insurer.id,
             description="Metformin, Glipizide, Calcium + Vitamin D3, pain management.",
             days_ago=90),
        dict(email="suresh@patient.com", policy="Senior Care Plan",
             claim_type="outpatient", amount_claimed=3500.0, status="approved",
             amount_approved=3500.0, reviewer=insurer.id,
             description="Diabetologist review, HbA1c, kidney function monitoring.",
             days_ago=50),
        dict(email="suresh@patient.com", policy="Senior Care Plan",
             claim_type="vision", amount_claimed=28000.0, status="approved",
             amount_approved=28000.0, reviewer=insurer.id,
             description="Cataract surgery — right eye — phacoemulsification at Sankara Nethralaya.",
             days_ago=20),

        # ── Kavya Iyer (young, no conditions) ──
        dict(email="kavya@patient.com", policy="Basic Health Plan",
             claim_type="outpatient", amount_claimed=700.0, status="approved",
             amount_approved=700.0, reviewer=insurer.id,
             description="General physician visit for UTI — antibiotics prescribed.",
             days_ago=12),

        # ── Rohit Gupta (heart disease + high cholesterol, 58) ──
        dict(email="rohit@patient.com", policy="Senior Care Plan",
             claim_type="hospitalization", amount_claimed=95000.0, status="approved",
             amount_approved=90000.0, reviewer=insurer.id,
             description="Elective coronary angioplasty (stent placement) at Medanta — 3-day stay.",
             days_ago=140),
        dict(email="rohit@patient.com", policy="Senior Care Plan",
             claim_type="prescription", amount_claimed=5400.0, status="approved",
             amount_approved=5400.0, reviewer=insurer.id,
             description="Rosuvastatin, Aspirin, Metoprolol, Ramipril — 3-month post-procedure.",
             days_ago=110),
        dict(email="rohit@patient.com", policy="Senior Care Plan",
             claim_type="laboratory", amount_claimed=3200.0, status="approved",
             amount_approved=3200.0, reviewer=insurer.id,
             description="Lipid profile, cardiac enzymes, ECG, echocardiogram.",
             days_ago=80),
        dict(email="rohit@patient.com", policy="Senior Care Plan",
             claim_type="outpatient", amount_claimed=4000.0, status="pending",
             description="Cardiologist consultation — routine 6-month cardiac follow-up.",
             days_ago=2),

        # ── Deepa Krishnan (PCOS + thyroid) ──
        dict(email="deepa@patient.com", policy="Maternity Plus Plan",
             claim_type="outpatient", amount_claimed=2800.0, status="approved",
             amount_approved=2800.0, reviewer=insurer.id,
             description="Gynaecologist consultation for PCOS management and hormonal workup.",
             days_ago=40),
        dict(email="deepa@patient.com", policy="Maternity Plus Plan",
             claim_type="laboratory", amount_claimed=4500.0, status="approved",
             amount_approved=4500.0, reviewer=insurer.id,
             description="PCOS panel: testosterone, DHEA-S, AMH, pelvic ultrasound.",
             days_ago=35),
        dict(email="deepa@patient.com", policy="Maternity Plus Plan",
             claim_type="prescription", amount_claimed=1200.0, status="approved",
             amount_approved=1200.0, reviewer=insurer.id,
             description="Metformin (PCOS), Levothyroxine, Folic acid supplementation.",
             days_ago=30),
        dict(email="deepa@patient.com", policy="Maternity Plus Plan",
             claim_type="maternity", amount_claimed=88000.0, status="under_review",
             description="Caesarean delivery at Cloudnine Hospital — 4-day stay. Complicated by gestational diabetes.",
             days_ago=5),

        # ── Anil Bhat (elderly: arthritis + cataract + diabetes) ──
        dict(email="anil@patient.com", policy="Senior Care Plan",
             claim_type="vision", amount_claimed=27500.0, status="approved",
             amount_approved=27500.0, reviewer=insurer.id,
             description="Left eye cataract surgery — IOL implant — at Aravind Eye Hospital.",
             days_ago=220),
        dict(email="anil@patient.com", policy="Senior Care Plan",
             claim_type="hospitalization", amount_claimed=145000.0, status="approved",
             amount_approved=140000.0, reviewer=insurer.id,
             description="Left hip replacement surgery at Hinduja Hospital — 6-day stay.",
             days_ago=190),
        dict(email="anil@patient.com", policy="Senior Care Plan",
             claim_type="prescription", amount_claimed=9800.0, status="approved",
             amount_approved=9800.0, reviewer=insurer.id,
             description="Insulin, Metformin, Calcium, DMARDs, proton pump inhibitor.",
             days_ago=150),
        dict(email="anil@patient.com", policy="Senior Care Plan",
             claim_type="physiotherapy", amount_claimed=18000.0, status="approved",
             amount_approved=18000.0, reviewer=insurer.id,
             description="Post-hip replacement physiotherapy — 24 sessions at Apollo PT.",
             days_ago=140),
        dict(email="anil@patient.com", policy="Senior Care Plan",
             claim_type="laboratory", amount_claimed=5500.0, status="approved",
             amount_approved=5500.0, reviewer=insurer.id,
             description="Comprehensive geriatric workup: HbA1c, renal, lipid, bone density scan.",
             days_ago=90),
        dict(email="anil@patient.com", policy="Senior Care Plan",
             claim_type="outpatient", amount_claimed=3200.0, status="pending",
             description="Rheumatologist and diabetologist dual consultation.",
             days_ago=3),

        # ── Sunita Verma (breast cancer remission) ──
        dict(email="sunita@patient.com", policy="Critical Illness Shield",
             claim_type="hospitalization", amount_claimed=320000.0, status="approved",
             amount_approved=300000.0, reviewer=insurer.id,
             description="Breast cancer lumpectomy + sentinel lymph node biopsy at Tata Memorial.",
             days_ago=95),
        dict(email="sunita@patient.com", policy="Critical Illness Shield",
             claim_type="prescription", amount_claimed=15000.0, status="approved",
             amount_approved=15000.0, reviewer=insurer.id,
             description="Tamoxifen 20mg (5-year hormonal therapy) — 3-month supply.",
             days_ago=70),
        dict(email="sunita@patient.com", policy="Critical Illness Shield",
             claim_type="outpatient", amount_claimed=6000.0, status="approved",
             amount_approved=6000.0, reviewer=insurer.id,
             description="Oncology follow-up — PET scan + tumour markers (CA 15-3).",
             days_ago=40),
        dict(email="sunita@patient.com", policy="Critical Illness Shield",
             claim_type="mental_health", amount_claimed=4500.0, status="approved",
             amount_approved=4500.0, reviewer=insurer.id,
             description="Psycho-oncology counselling — 6 sessions for post-cancer anxiety.",
             days_ago=20),

        # ── Kiran Rao (kidney disease, smoker) ──
        dict(email="kiran@patient.com", policy="Premium Health Plan",
             claim_type="hospitalization", amount_claimed=90000.0, status="approved",
             amount_approved=85000.0, reviewer=insurer.id,
             description="Acute kidney injury (AKI) — 4-day nephrology ward admission at St. John's.",
             days_ago=120),
        dict(email="kiran@patient.com", policy="Premium Health Plan",
             claim_type="prescription", amount_claimed=7800.0, status="approved",
             amount_approved=7800.0, reviewer=insurer.id,
             description="Tacrolimus, Mycophenolate, antihypertensives, Erythropoietin.",
             days_ago=100),
        dict(email="kiran@patient.com", policy="Premium Health Plan",
             claim_type="laboratory", amount_claimed=5500.0, status="approved",
             amount_approved=5500.0, reviewer=insurer.id,
             description="Kidney function tests: creatinine, urea, eGFR, urine protein — monthly.",
             days_ago=70),
        dict(email="kiran@patient.com", policy="Premium Health Plan",
             claim_type="hospitalization", amount_claimed=18000.0, status="pending",
             description="Kidney biopsy (outpatient procedure) at St. John's Medical College.",
             days_ago=6),

        # ── Pooja Joshi (depression + anxiety) ──
        dict(email="pooja@patient.com", policy="Standard Health Plan",
             claim_type="mental_health", amount_claimed=6000.0, status="approved",
             amount_approved=6000.0, reviewer=insurer.id,
             description="Psychiatrist consultation + 8 CBT therapy sessions for GAD.",
             days_ago=50),
        dict(email="pooja@patient.com", policy="Standard Health Plan",
             claim_type="prescription", amount_claimed=1400.0, status="approved",
             amount_approved=1400.0, reviewer=insurer.id,
             description="Sertraline 50mg and Clonazepam 0.5mg — 2-month supply.",
             days_ago=40),
        dict(email="pooja@patient.com", policy="Standard Health Plan",
             claim_type="outpatient", amount_claimed=1800.0, status="approved",
             amount_approved=1800.0, reviewer=insurer.id,
             description="Psychiatrist follow-up for medication adjustment.",
             days_ago=15),

        # ── Ramesh Chauhan (COPD + hypertension, smoker) ──
        dict(email="ramesh@patient.com", policy="Senior Care Plan",
             claim_type="hospitalization", amount_claimed=65000.0, status="approved",
             amount_approved=60000.0, reviewer=insurer.id,
             description="COPD exacerbation — 3-day hospitalization with IV steroids and nebulization.",
             days_ago=150),
        dict(email="ramesh@patient.com", policy="Senior Care Plan",
             claim_type="prescription", amount_claimed=4200.0, status="approved",
             amount_approved=4200.0, reviewer=insurer.id,
             description="Tiotropium inhaler, Formoterol-Budesonide, Amlodipine, oral steroids.",
             days_ago=130),
        dict(email="ramesh@patient.com", policy="Senior Care Plan",
             claim_type="laboratory", amount_claimed=3800.0, status="approved",
             amount_approved=3800.0, reviewer=insurer.id,
             description="Spirometry, ABG analysis, chest X-ray, CBC — pulmonology workup.",
             days_ago=100),
        dict(email="ramesh@patient.com", policy="Senior Care Plan",
             claim_type="hospitalization", amount_claimed=78000.0, status="pending",
             description="Severe COPD exacerbation — ICU admission with BiPAP support.",
             days_ago=4),

        # ── Nisha Agarwal (anemia, maternity) ──
        dict(email="nisha@patient.com", policy="Maternity Plus Plan",
             claim_type="maternity", amount_claimed=52000.0, status="approved",
             amount_approved=48000.0, reviewer=insurer.id,
             description="Normal delivery at Cloudnine Hospital — 2-day stay. Iron transfusion pre-delivery.",
             days_ago=18),
        dict(email="nisha@patient.com", policy="Maternity Plus Plan",
             claim_type="laboratory", amount_claimed=2800.0, status="approved",
             amount_approved=2800.0, reviewer=insurer.id,
             description="Antenatal workup: CBC, ferritin, folate, anomaly scan, NIPT.",
             days_ago=50),
        dict(email="nisha@patient.com", policy="Maternity Plus Plan",
             claim_type="prescription", amount_claimed=1600.0, status="approved",
             amount_approved=1600.0, reviewer=insurer.id,
             description="Iron sucrose infusion, Folic acid, Calcium — antenatal supplements.",
             days_ago=35),

        # ── Sanjay Malhotra (obesity + hypertension + sleep apnea) ──
        dict(email="sanjay@patient.com", policy="Family Floater Plan",
             claim_type="outpatient", amount_claimed=4500.0, status="approved",
             amount_approved=4500.0, reviewer=insurer.id,
             description="Sleep study (polysomnography) for sleep apnea diagnosis at Apollo Sleep Lab.",
             days_ago=100),
        dict(email="sanjay@patient.com", policy="Family Floater Plan",
             claim_type="prescription", amount_claimed=12000.0, status="approved",
             amount_approved=12000.0, reviewer=insurer.id,
             description="CPAP machine rental + Telmisartan 80mg — 6-month supply.",
             days_ago=85),
        dict(email="sanjay@patient.com", policy="Family Floater Plan",
             claim_type="hospitalization", amount_claimed=180000.0, status="approved",
             amount_approved=165000.0, reviewer=insurer.id,
             description="Laparoscopic sleeve gastrectomy (bariatric surgery) at Fortis — 3-day stay.",
             days_ago=60),
        dict(email="sanjay@patient.com", policy="Family Floater Plan",
             claim_type="outpatient", amount_claimed=5500.0, status="approved",
             amount_approved=5500.0, reviewer=insurer.id,
             description="Post-bariatric follow-up: nutritionist, endocrinologist, BP monitoring.",
             days_ago=30),
        dict(email="sanjay@patient.com", policy="Family Floater Plan",
             claim_type="laboratory", amount_claimed=3800.0, status="pending",
             description="Post-surgery metabolic panel: B12, Iron, Zinc, Calcium, Vitamin D.",
             days_ago=2),
    ]

    created = 0
    notifications_to_add = []

    for cd in raw_claims:
        patient = users.get(cd["email"])
        # Skip if this patient already has claims
        if not patient or cd["email"] not in patients_needing_claims:
            continue
        policy_obj = policies_map.get(cd["policy"]) or fallback
        if not policy_obj:
            continue

        risk_score, risk_level = calculate_risk_score(
            age=patient.age,
            bmi=patient.bmi,
            is_smoker=patient.is_smoker,
            conditions=patient.get_conditions(),
            claim_amount=cd["amount_claimed"],
            policy_max=policy_obj.max_coverage_limit,
        )

        claim = Claim(
            patient_id=patient.id,
            policy_id=policy_obj.id,
            claim_type=cd["claim_type"],
            description=cd["description"],
            amount_claimed=cd["amount_claimed"],
            amount_approved=cd.get("amount_approved"),
            status=cd["status"],
            risk_score=risk_score,
            risk_level=risk_level,
            reviewer_id=cd.get("reviewer"),
            rejection_reason=cd.get("rejection_reason"),
            created_at=datetime.utcnow() - timedelta(days=cd["days_ago"]),
            updated_at=datetime.utcnow() - timedelta(days=max(0, cd["days_ago"] - 2)),
        )
        db.add(claim)
        db.flush()  # get claim.id

        # Auto-generate notifications
        if cd["status"] == "approved":
            notifications_to_add.append(Notification(
                user_id=patient.id,
                title="Claim Approved",
                message=f"Your {cd['claim_type']} claim of ₹{cd['amount_claimed']:,.0f} has been approved. Approved: ₹{cd.get('amount_approved', 0):,.0f}.",
                notification_type="claim_approved",
                is_read=cd["days_ago"] > 10,
                related_entity_type="claim",
                related_entity_id=claim.id,
                created_at=datetime.utcnow() - timedelta(days=max(0, cd["days_ago"] - 2)),
            ))
        elif cd["status"] == "rejected":
            notifications_to_add.append(Notification(
                user_id=patient.id,
                title="Claim Rejected",
                message=f"Your {cd['claim_type']} claim of ₹{cd['amount_claimed']:,.0f} was rejected. Reason: {cd.get('rejection_reason', 'See details.')}",
                notification_type="claim_rejected",
                is_read=cd["days_ago"] > 10,
                related_entity_type="claim",
                related_entity_id=claim.id,
                created_at=datetime.utcnow() - timedelta(days=max(0, cd["days_ago"] - 2)),
            ))
        elif cd["status"] in ("pending", "under_review"):
            notifications_to_add.append(Notification(
                user_id=insurer.id,
                title="New Claim Submitted",
                message=f"{patient.full_name} submitted a {cd['claim_type']} claim of ₹{cd['amount_claimed']:,.0f} (Risk: {risk_level}).",
                notification_type="claim_submitted",
                is_read=False,
                related_entity_type="claim",
                related_entity_id=claim.id,
                created_at=datetime.utcnow() - timedelta(days=max(0, cd["days_ago"] - 1)),
            ))

        created += 1

    for n in notifications_to_add:
        db.add(n)

    db.commit()
    print(f"Demo claims seeded: {created} claims and {len(notifications_to_add)} notifications created.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    db = SessionLocal()
    try:
        try:
            from knowledge_base.seed_policies import seed
            seed()
        except Exception as e:
            print(f"Seed failed: {e}")

        _seed_demo_users(db)
        try:
            _seed_demo_claims(db)
        except Exception as e:
            print(f"Claims seed failed: {e}")
    finally:
        db.close()

    yield


app = FastAPI(
    title="Health Insurance Management System",
    description="Full-featured health insurance management with RAG-powered eligibility chat",
    version="1.0.0",
    lifespan=lifespan,
)

frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:4200")
allowed_origins = [origin.strip() for origin in frontend_url.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(eligibility.router, prefix="/api/chat", tags=["Eligibility Chat"])
app.include_router(claims.router, prefix="/api/claims", tags=["Claims"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(premium.router, prefix="/api/premium", tags=["Premium"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
