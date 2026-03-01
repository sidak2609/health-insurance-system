import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import create_tables, SessionLocal
from app.db.models import Policy
from app.api.routes import auth, eligibility, claims, policies, dashboard, premium, documents, notifications


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
