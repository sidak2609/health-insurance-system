from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, Claim, Policy, Notification
from app.models.schemas import ClaimCreate, ClaimReview, ClaimResponse
from app.services.auth_service import get_current_user, require_role
from app.services.risk_scoring import calculate_risk_score
from app.services.audit_service import log_action

router = APIRouter()


def claim_to_response(claim: Claim, db: Session) -> ClaimResponse:
    patient = db.query(User).filter(User.id == claim.patient_id).first()
    policy = db.query(Policy).filter(Policy.id == claim.policy_id).first()
    return ClaimResponse(
        id=claim.id,
        patient_id=claim.patient_id,
        policy_id=claim.policy_id,
        claim_type=claim.claim_type,
        description=claim.description,
        amount_claimed=claim.amount_claimed,
        amount_approved=claim.amount_approved,
        status=claim.status,
        risk_score=claim.risk_score,
        risk_level=claim.risk_level,
        reviewer_id=claim.reviewer_id,
        rejection_reason=claim.rejection_reason,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
        patient_name=patient.full_name if patient else None,
        policy_name=policy.name if policy else None,
    )


@router.post("", response_model=ClaimResponse)
def submit_claim(
    data: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    policy = db.query(Policy).filter(Policy.id == data.policy_id, Policy.is_active == True).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Calculate risk score
    risk_score, risk_level = calculate_risk_score(
        age=current_user.age,
        bmi=current_user.bmi,
        is_smoker=current_user.is_smoker,
        conditions=current_user.get_conditions(),
        claim_amount=data.amount_claimed,
        policy_max=policy.max_coverage_limit,
    )

    claim = Claim(
        patient_id=current_user.id,
        policy_id=data.policy_id,
        claim_type=data.claim_type,
        description=data.description,
        amount_claimed=data.amount_claimed,
        risk_score=risk_score,
        risk_level=risk_level,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    log_action(db, "claim_submitted", current_user.id, "claim", claim.id, {
        "amount": data.amount_claimed, "risk_level": risk_level,
    })

    # Notify insurers
    insurers = db.query(User).filter(User.role == "insurer").all()
    for insurer in insurers:
        notif = Notification(
            user_id=insurer.id,
            title="New Claim Submitted",
            message=f"A new {data.claim_type} claim for ${data.amount_claimed:,.2f} has been submitted (Risk: {risk_level}).",
            notification_type="claim_submitted",
            related_entity_type="claim",
            related_entity_id=claim.id,
        )
        db.add(notif)
    db.commit()

    return claim_to_response(claim, db)


@router.get("", response_model=list[ClaimResponse])
def list_claims(
    status: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Claim)

    if current_user.role == "patient":
        query = query.filter(Claim.patient_id == current_user.id)

    if status:
        query = query.filter(Claim.status == status)

    claims = query.order_by(Claim.created_at.desc()).all()
    return [claim_to_response(c, db) for c in claims]


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if current_user.role == "patient" and claim.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return claim_to_response(claim, db)


@router.put("/{claim_id}/review", response_model=ClaimResponse)
def review_claim(
    claim_id: int,
    data: ClaimReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("insurer")),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.status = data.status
    claim.reviewer_id = current_user.id

    if data.status == "approved":
        claim.amount_approved = data.amount_approved or claim.amount_claimed
    elif data.status == "rejected":
        claim.rejection_reason = data.rejection_reason

    db.commit()
    db.refresh(claim)

    # Store values now to avoid lazy-load issues after log_action's commit
    patient_id = claim.patient_id
    claim_type = claim.claim_type
    claim_id_val = claim.id
    amount_approved = claim.amount_approved
    rejection_reason = claim.rejection_reason

    log_action(db, f"claim_{data.status}", current_user.id, "claim", claim_id_val, {
        "amount_approved": amount_approved,
        "rejection_reason": rejection_reason,
    })

    # Notify patient
    status_label = "approved" if data.status == "approved" else "rejected"
    msg = f"Your {claim_type} claim #{claim_id_val} has been {status_label}."
    if data.status == "approved" and amount_approved is not None:
        msg += f" Approved amount: ₹{amount_approved:,.2f}"
    if rejection_reason:
        msg += f" Reason: {rejection_reason}"

    notif = Notification(
        user_id=patient_id,
        title=f"Claim {status_label.title()}",
        message=msg,
        notification_type=f"claim_{status_label}",
        related_entity_type="claim",
        related_entity_id=claim_id_val,
    )
    db.add(notif)
    db.commit()

    return claim_to_response(claim, db)
