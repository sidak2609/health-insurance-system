import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.models.schemas import UserRegister, UserLogin, TokenResponse, UserProfile
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user
from app.services.audit_service import log_action

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        age=data.age,
        bmi=data.bmi,
        is_smoker=data.is_smoker,
        pre_existing_conditions=json.dumps(data.pre_existing_conditions),
        company_name=data.company_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_action(db, "user_registered", user.id, "user", user.id, {"role": user.role})

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    log_action(db, "user_login", user.id, "user", user.id)

    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
    )


@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        age=current_user.age,
        bmi=current_user.bmi,
        is_smoker=current_user.is_smoker,
        pre_existing_conditions=current_user.get_conditions(),
        company_name=current_user.company_name,
        created_at=current_user.created_at,
    )
