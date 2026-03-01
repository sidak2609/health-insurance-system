from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, Policy
from app.models.schemas import PremiumEstimateRequest, PremiumEstimateResponse, PremiumBreakdown
from app.services.auth_service import get_current_user
from app.services.premium_calculator import estimate_premium

router = APIRouter()


@router.post("/estimate", response_model=PremiumEstimateResponse)
def estimate(
    data: PremiumEstimateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Policy).filter(Policy.is_active == True)
    if data.policy_ids:
        query = query.filter(Policy.id.in_(data.policy_ids))

    policies = query.all()
    estimates = []
    for policy in policies:
        breakdown = estimate_premium(
            policy=policy,
            age=data.age,
            bmi=data.bmi,
            is_smoker=data.is_smoker,
            conditions=data.pre_existing_conditions,
        )
        estimates.append(PremiumBreakdown(**breakdown))

    return PremiumEstimateResponse(estimates=estimates)
