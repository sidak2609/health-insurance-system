from enum import Enum


class UserRole(str, Enum):
    patient = "patient"
    insurer = "insurer"


class ClaimStatus(str, Enum):
    pending = "pending"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    paid = "paid"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class DocumentType(str, Enum):
    medical_record = "medical_record"
    prescription = "prescription"
    lab_result = "lab_result"
    insurance_card = "insurance_card"
    claim_receipt = "claim_receipt"
    other = "other"
