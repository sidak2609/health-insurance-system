import json
from collections import Counter, defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, Claim, AuditLog
from app.models.schemas import (
    DashboardResponse, DashboardStats, DashboardTrend,
    DemographicBreakdown, AuditLogResponse,
)
from app.services.auth_service import require_role

router = APIRouter()


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("insurer")),
):
    claims = db.query(Claim).all()

    total = len(claims)
    approved = sum(1 for c in claims if c.status == "approved")
    rejected = sum(1 for c in claims if c.status == "rejected")
    pending = sum(1 for c in claims if c.status in ("pending", "under_review"))
    high_risk = sum(1 for c in claims if c.risk_level == "high")
    total_claimed = sum(c.amount_claimed for c in claims)
    total_approved_amt = sum(c.amount_approved or 0 for c in claims if c.status == "approved")

    stats = DashboardStats(
        total_claims=total,
        approved_count=approved,
        rejected_count=rejected,
        pending_count=pending,
        high_risk_count=high_risk,
        total_amount_claimed=round(total_claimed, 2),
        total_amount_approved=round(total_approved_amt, 2),
        approval_rate=round(approved / total * 100, 1) if total else 0,
        rejection_rate=round(rejected / total * 100, 1) if total else 0,
    )

    # Monthly trends
    monthly = defaultdict(lambda: {"count": 0, "amount": 0.0})
    for c in claims:
        key = c.created_at.strftime("%Y-%m")
        monthly[key]["count"] += 1
        monthly[key]["amount"] += c.amount_claimed
    monthly_trends = [
        DashboardTrend(month=k, count=v["count"], amount=round(v["amount"], 2))
        for k, v in sorted(monthly.items())
    ]

    # Age demographics
    age_buckets = Counter()
    for c in claims:
        patient = db.query(User).filter(User.id == c.patient_id).first()
        if patient and patient.age:
            if patient.age < 30:
                age_buckets["18-29"] += 1
            elif patient.age < 40:
                age_buckets["30-39"] += 1
            elif patient.age < 50:
                age_buckets["40-49"] += 1
            elif patient.age < 60:
                age_buckets["50-59"] += 1
            else:
                age_buckets["60+"] += 1
    age_demographics = [DemographicBreakdown(label=k, count=v) for k, v in sorted(age_buckets.items())]

    # Top conditions
    condition_counter = Counter()
    for c in claims:
        patient = db.query(User).filter(User.id == c.patient_id).first()
        if patient:
            for cond in patient.get_conditions():
                condition_counter[cond] += 1
    top_conditions = [
        DemographicBreakdown(label=k, count=v)
        for k, v in condition_counter.most_common(10)
    ]

    # Top claim types
    type_counter = Counter(c.claim_type for c in claims)
    top_claim_types = [
        DemographicBreakdown(label=k, count=v)
        for k, v in type_counter.most_common(10)
    ]

    # Claims by status — merge pending and under_review into one bucket
    status_counter = Counter()
    for c in claims:
        if c.status in ("pending", "under_review"):
            status_counter["Pending Review"] += 1
        elif c.status == "approved":
            status_counter["Approved"] += 1
        elif c.status == "rejected":
            status_counter["Rejected"] += 1
        else:
            status_counter[c.status.replace("_", " ").title()] += 1
    claims_by_status = [DemographicBreakdown(label=k, count=v) for k, v in status_counter.items()]

    # Claims by policy
    from app.db.models import Policy
    policy_counter = Counter()
    for c in claims:
        policy = db.query(Policy).filter(Policy.id == c.policy_id).first()
        if policy:
            policy_counter[policy.name] += 1
    claims_by_policy = [DemographicBreakdown(label=k, count=v) for k, v in policy_counter.items()]

    return DashboardResponse(
        stats=stats,
        monthly_trends=monthly_trends,
        age_demographics=age_demographics,
        top_conditions=top_conditions,
        top_claim_types=top_claim_types,
        claims_by_status=claims_by_status,
        claims_by_policy=claims_by_policy,
    )


@router.get("/audit", response_model=list[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("insurer")),
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    result = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first() if log.user_id else None
        try:
            details = json.loads(log.details or "{}")
        except (json.JSONDecodeError, TypeError):
            details = {}
        result.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_name=user.full_name if user else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=details,
            created_at=log.created_at,
        ))
    return result
