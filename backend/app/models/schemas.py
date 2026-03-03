from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- Auth ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "patient"
    age: Optional[int] = None
    bmi: Optional[float] = None
    is_smoker: bool = False
    pre_existing_conditions: list[str] = []
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    full_name: str


class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    age: Optional[int] = None
    bmi: Optional[float] = None
    is_smoker: bool = False
    pre_existing_conditions: list[str] = []
    company_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Policy ---
class PolicySectionCreate(BaseModel):
    section_title: str
    section_content: str
    section_number: int
    keywords: list[str] = []


class PolicySectionResponse(BaseModel):
    id: int
    section_title: str
    section_content: str
    section_number: int
    keywords: list[str] = []

    class Config:
        from_attributes = True


class PolicyCreate(BaseModel):
    name: str
    plan_type: str
    monthly_premium_base: float
    annual_deductible: float
    max_coverage_limit: float
    copay_percentage: float
    coverage_details: list[str] = []
    exclusions: list[str] = []
    age_min: int = 18
    age_max: int = 65
    smoker_surcharge_pct: float = 0.0
    bmi_surcharge_pct: float = 0.0
    pre_existing_waiting_months: int = 12


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    plan_type: Optional[str] = None
    monthly_premium_base: Optional[float] = None
    annual_deductible: Optional[float] = None
    max_coverage_limit: Optional[float] = None
    copay_percentage: Optional[float] = None
    coverage_details: Optional[list[str]] = None
    exclusions: Optional[list[str]] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    smoker_surcharge_pct: Optional[float] = None
    bmi_surcharge_pct: Optional[float] = None
    pre_existing_waiting_months: Optional[int] = None


class PolicyResponse(BaseModel):
    id: int
    name: str
    plan_type: str
    monthly_premium_base: float
    annual_deductible: float
    max_coverage_limit: float
    copay_percentage: float
    coverage_details: list[str] = []
    exclusions: list[str] = []
    age_min: int
    age_max: int
    smoker_surcharge_pct: float
    bmi_surcharge_pct: float
    pre_existing_waiting_months: int
    is_active: bool
    sections: list[PolicySectionResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# --- Claims ---
class ClaimCreate(BaseModel):
    policy_id: int
    claim_type: str
    description: Optional[str] = None
    amount_claimed: float


class ClaimReview(BaseModel):
    status: str  # approved / rejected
    amount_approved: Optional[float] = None
    rejection_reason: Optional[str] = None


class ClaimResponse(BaseModel):
    id: int
    patient_id: int
    policy_id: int
    claim_type: str
    description: Optional[str] = None
    amount_claimed: float
    amount_approved: Optional[float] = None
    status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    reviewer_id: Optional[int] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    patient_name: Optional[str] = None
    policy_name: Optional[str] = None

    class Config:
        from_attributes = True


# --- Chat / RAG ---
class CitationItem(BaseModel):
    policy_name: str
    section_title: str
    section_number: int
    excerpt: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: int
    message: str
    citations: list[CitationItem] = []
    follow_up_questions: list[str] = []


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    citations: list[CitationItem] = []
    follow_up_questions: list[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


# --- Premium ---
class PremiumEstimateRequest(BaseModel):
    age: int
    bmi: float
    is_smoker: bool = False
    pre_existing_conditions: list[str] = []
    policy_ids: Optional[list[int]] = None


class PremiumBreakdown(BaseModel):
    policy_id: int
    policy_name: str
    plan_type: str
    base_premium: float
    age_adjustment: float
    bmi_adjustment: float
    smoker_adjustment: float
    condition_adjustment: float
    final_monthly_premium: float
    annual_deductible: float
    max_coverage: float
    copay_percentage: float


class PremiumEstimateResponse(BaseModel):
    estimates: list[PremiumBreakdown]


# --- Notifications ---
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Dashboard ---
class DashboardStats(BaseModel):
    total_claims: int
    approved_count: int
    rejected_count: int
    pending_count: int
    high_risk_count: int
    total_amount_claimed: float
    total_amount_approved: float
    approval_rate: float
    rejection_rate: float


class DashboardTrend(BaseModel):
    month: str
    count: int
    amount: float


class DemographicBreakdown(BaseModel):
    label: str
    count: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    monthly_trends: list[DashboardTrend]
    age_demographics: list[DemographicBreakdown]
    top_conditions: list[DemographicBreakdown]
    top_claim_types: list[DemographicBreakdown]
    claims_by_status: list[DemographicBreakdown]
    claims_by_policy: list[DemographicBreakdown]


# --- Audit ---
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True


# --- Documents ---
class DocumentResponse(BaseModel):
    id: int
    filename: str
    document_type: str
    is_indexed: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True
