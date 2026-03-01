import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, Policy, PolicySection
from app.models.schemas import (
    PolicyCreate, PolicyUpdate, PolicyResponse, PolicySectionCreate, PolicySectionResponse,
)
from app.services.auth_service import get_current_user, require_role
from app.services.audit_service import log_action
from app.rag.ingest import build_vector_store

router = APIRouter()


def policy_to_response(policy: Policy) -> PolicyResponse:
    sections = []
    for s in sorted(policy.sections, key=lambda x: x.section_number):
        try:
            kw = json.loads(s.keywords or "[]")
        except (json.JSONDecodeError, TypeError):
            kw = []
        sections.append(PolicySectionResponse(
            id=s.id,
            section_title=s.section_title,
            section_content=s.section_content,
            section_number=s.section_number,
            keywords=kw,
        ))

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        plan_type=policy.plan_type,
        monthly_premium_base=policy.monthly_premium_base,
        annual_deductible=policy.annual_deductible,
        max_coverage_limit=policy.max_coverage_limit,
        copay_percentage=policy.copay_percentage,
        coverage_details=policy.get_coverage(),
        exclusions=policy.get_exclusions(),
        age_min=policy.age_min,
        age_max=policy.age_max,
        smoker_surcharge_pct=policy.smoker_surcharge_pct,
        bmi_surcharge_pct=policy.bmi_surcharge_pct,
        pre_existing_waiting_months=policy.pre_existing_waiting_months,
        is_active=policy.is_active,
        sections=sections,
        created_at=policy.created_at,
    )


@router.get("", response_model=list[PolicyResponse])
def list_policies(db: Session = Depends(get_db)):
    policies = db.query(Policy).filter(Policy.is_active == True).all()
    return [policy_to_response(p) for p in policies]


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy_to_response(policy)


@router.post("", response_model=PolicyResponse)
def create_policy(
    data: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("insurer")),
):
    policy = Policy(
        name=data.name,
        plan_type=data.plan_type,
        monthly_premium_base=data.monthly_premium_base,
        annual_deductible=data.annual_deductible,
        max_coverage_limit=data.max_coverage_limit,
        copay_percentage=data.copay_percentage,
        coverage_details=json.dumps(data.coverage_details),
        exclusions=json.dumps(data.exclusions),
        age_min=data.age_min,
        age_max=data.age_max,
        smoker_surcharge_pct=data.smoker_surcharge_pct,
        bmi_surcharge_pct=data.bmi_surcharge_pct,
        pre_existing_waiting_months=data.pre_existing_waiting_months,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    log_action(db, "policy_created", current_user.id, "policy", policy.id, {"name": policy.name})
    return policy_to_response(policy)


@router.post("/{policy_id}/sections", response_model=PolicySectionResponse)
def add_section(
    policy_id: int,
    data: PolicySectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("insurer")),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    section = PolicySection(
        policy_id=policy_id,
        section_title=data.section_title,
        section_content=data.section_content,
        section_number=data.section_number,
        keywords=json.dumps(data.keywords),
    )
    db.add(section)
    db.commit()
    db.refresh(section)

    # Rebuild FAISS index
    try:
        build_vector_store(db)
    except Exception as e:
        print(f"Failed to rebuild vector store: {e}")

    log_action(db, "section_added", current_user.id, "policy_section", section.id, {
        "policy_id": policy_id, "title": data.section_title,
    })

    return PolicySectionResponse(
        id=section.id,
        section_title=section.section_title,
        section_content=section.section_content,
        section_number=section.section_number,
        keywords=data.keywords,
    )


@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: int,
    data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("insurer")),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = data.model_dump(exclude_unset=True)
    if "coverage_details" in update_data:
        update_data["coverage_details"] = json.dumps(update_data["coverage_details"])
    if "exclusions" in update_data:
        update_data["exclusions"] = json.dumps(update_data["exclusions"])

    for key, value in update_data.items():
        setattr(policy, key, value)

    db.commit()
    db.refresh(policy)

    log_action(db, "policy_updated", current_user.id, "policy", policy.id, {"fields": list(update_data.keys())})
    return policy_to_response(policy)


@router.delete("/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("insurer")),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.is_active = False
    db.commit()

    log_action(db, "policy_deleted", current_user.id, "policy", policy.id, {"name": policy.name})
    return {"message": "Policy deactivated"}
