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
    if db.query(User).count() > 0:
        return
    users = [
        User(email="rajesh@patient.com", hashed_password=hash_password("password123"),
             full_name="Rajesh Kumar", role="patient", age=35, bmi=26.2, is_smoker=False,
             pre_existing_conditions=json.dumps(["diabetes", "hypertension"]),
             created_at=datetime.utcnow() - timedelta(days=45)),
        User(email="priya@patient.com", hashed_password=hash_password("password123"),
             full_name="Priya Sharma", role="patient", age=28, bmi=22.1, is_smoker=True,
             pre_existing_conditions=json.dumps(["asthma"]),
             created_at=datetime.utcnow() - timedelta(days=30)),
        User(email="admin@insurer.com", hashed_password=hash_password("password123"),
             full_name="Dr. Amit Patel", role="insurer", company_name="Star Health Insurance",
             created_at=datetime.utcnow() - timedelta(days=90)),
    ]
    for u in users:
        db.add(u)
    db.commit()
    print("Demo users seeded.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    db = SessionLocal()
    try:
        if db.query(Policy).count() == 0:
            print("Empty database detected. Running seed...")
            from knowledge_base.seed_policies import seed
            seed()
        else:
            try:
                from app.rag.ingest import build_vector_store
                build_vector_store(db)
                print("FAISS vector store rebuilt from existing data.")
            except Exception as e:
                print(f"Failed to build vector store: {e}")

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
