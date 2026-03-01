import json
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # patient / insurer
    age = Column(Integer, nullable=True)
    bmi = Column(Float, nullable=True)
    is_smoker = Column(Boolean, default=False)
    pre_existing_conditions = Column(Text, default="[]")  # JSON list
    company_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    claims = relationship("Claim", back_populates="patient", foreign_keys="Claim.patient_id")
    documents = relationship("Document", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

    def get_conditions(self):
        try:
            return json.loads(self.pre_existing_conditions or "[]")
        except (json.JSONDecodeError, TypeError):
            return []


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plan_type = Column(String, nullable=False)  # basic / standard / premium
    monthly_premium_base = Column(Float, nullable=False)
    annual_deductible = Column(Float, nullable=False)
    max_coverage_limit = Column(Float, nullable=False)
    copay_percentage = Column(Float, nullable=False)
    coverage_details = Column(Text, default="[]")  # JSON list
    exclusions = Column(Text, default="[]")  # JSON list
    age_min = Column(Integer, default=18)
    age_max = Column(Integer, default=65)
    smoker_surcharge_pct = Column(Float, default=0.0)
    bmi_surcharge_pct = Column(Float, default=0.0)
    pre_existing_waiting_months = Column(Integer, default=12)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sections = relationship("PolicySection", back_populates="policy", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="policy")

    def get_coverage(self):
        try:
            return json.loads(self.coverage_details or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def get_exclusions(self):
        try:
            return json.loads(self.exclusions or "[]")
        except (json.JSONDecodeError, TypeError):
            return []


class PolicySection(Base):
    __tablename__ = "policy_sections"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    section_title = Column(String, nullable=False)
    section_content = Column(Text, nullable=False)
    section_number = Column(Integer, nullable=False)
    keywords = Column(Text, default="[]")  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)

    policy = relationship("Policy", back_populates="sections")

    def get_keywords(self):
        try:
            return json.loads(self.keywords or "[]")
        except (json.JSONDecodeError, TypeError):
            return []


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    claim_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    amount_claimed = Column(Float, nullable=False)
    amount_approved = Column(Float, nullable=True)
    status = Column(String, default="pending")
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("User", back_populates="claims", foreign_keys=[patient_id])
    policy = relationship("Policy", back_populates="claims")
    reviewer = relationship("User", foreign_keys=[reviewer_id])


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    is_indexed = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="documents")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String, nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, default="{}")  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    citations = Column(Text, default="[]")  # JSON list
    follow_up_questions = Column(Text, default="[]")  # JSON list
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
