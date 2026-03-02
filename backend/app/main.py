import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import json
from datetime import datetime, timedelta

from app.db.database import create_tables, SessionLocal
from app.db.models import Policy, User
from app.api.routes import auth, eligibility, claims, policies, dashboard, premium, documents, notifications


def _seed_demo_users(db):
    from app.services.auth_service import hash_password

    demo_emails = [
        "rajesh@patient.com", "priya@patient.com", "arjun@patient.com",
        "meera@patient.com", "vikram@patient.com", "ananya@patient.com",
        "suresh@patient.com", "admin@insurer.com",
    ]
    existing_emails = {u.email for u in db.query(User).all()}
    if all(e in existing_emails for e in demo_emails):
        return  # All demo users already exist

    demo_users = [
        # Patients
        User(email="rajesh@patient.com", hashed_password=hash_password("password123"),
             full_name="Rajesh Kumar", role="patient", age=35, bmi=26.2, is_smoker=False,
             pre_existing_conditions=json.dumps(["diabetes", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=45)),
        User(email="priya@patient.com", hashed_password=hash_password("password123"),
             full_name="Priya Sharma", role="patient", age=28, bmi=22.1, is_smoker=True,
             pre_existing_conditions=json.dumps(["asthma"]),
             created_at=datetime.utcnow() - timedelta(days=30)),
        User(email="arjun@patient.com", hashed_password=hash_password("password123"),
             full_name="Arjun Mehta", role="patient", age=52, bmi=31.5, is_smoker=True,
             pre_existing_conditions=json.dumps(["diabetes", "heart_disease", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=60)),
        User(email="meera@patient.com", hashed_password=hash_password("password123"),
             full_name="Meera Nair", role="patient", age=31, bmi=23.8, is_smoker=False,
             pre_existing_conditions=json.dumps(["thyroid"]),
             created_at=datetime.utcnow() - timedelta(days=20)),
        User(email="vikram@patient.com", hashed_password=hash_password("password123"),
             full_name="Vikram Singh", role="patient", age=45, bmi=28.4, is_smoker=False,
             pre_existing_conditions=json.dumps(["back_pain", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=15)),
        User(email="ananya@patient.com", hashed_password=hash_password("password123"),
             full_name="Ananya Reddy", role="patient", age=26, bmi=20.5, is_smoker=False,
             pre_existing_conditions=json.dumps([]),
             created_at=datetime.utcnow() - timedelta(days=10)),
        User(email="suresh@patient.com", hashed_password=hash_password("password123"),
             full_name="Suresh Pillai", role="patient", age=62, bmi=27.9, is_smoker=False,
             pre_existing_conditions=json.dumps(["arthritis", "diabetes"]),
             created_at=datetime.utcnow() - timedelta(days=80)),
        # Insurer
        User(email="admin@insurer.com", hashed_password=hash_password("password123"),
             full_name="Dr. Amit Patel", role="insurer", company_name="Star Health Insurance",
             created_at=datetime.utcnow() - timedelta(days=90)),
    ]

    added = 0
    for u in demo_users:
        if u.email not in existing_emails:
            db.add(u)
            added += 1
    db.commit()
    print(f"Demo users seeded: {added} new users added.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    db = SessionLocal()
    try:
        # Always run seed — it upserts policies/sections and is safe to re-run.
        # This ensures new knowledge base sections are applied on every deploy.
        try:
            from knowledge_base.seed_policies import seed
            seed()
        except Exception as e:
            print(f"Seed failed: {e}")

        _seed_demo_users(db)
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
