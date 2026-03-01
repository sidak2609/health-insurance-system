import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse, ChatSessionResponse, ChatMessageResponse, CitationItem
from app.services.auth_service import get_current_user
from app.rag.pipeline import process_chat_message
from app.services.pdf_generator import generate_eligibility_report

router = APIRouter()


@router.post("", response_model=ChatResponse)
def send_message(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient_details = {
        "age": current_user.age,
        "bmi": current_user.bmi,
        "is_smoker": current_user.is_smoker,
        "conditions": current_user.get_conditions(),
    }

    return process_chat_message(
        db=db,
        user_id=current_user.id,
        message=data.message,
        session_id=data.session_id,
        patient_details=patient_details,
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    result = []
    for s in sessions:
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        result.append(ChatSessionResponse(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            message_count=msg_count,
        ))
    return result


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    result = []
    for msg in messages:
        try:
            citations = [CitationItem(**c) for c in json.loads(msg.citations or "[]")]
        except (json.JSONDecodeError, TypeError):
            citations = []
        try:
            follow_ups = json.loads(msg.follow_up_questions or "[]")
        except (json.JSONDecodeError, TypeError):
            follow_ups = []

        result.append(ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            citations=citations,
            follow_up_questions=follow_ups,
            created_at=msg.created_at,
        ))
    return result


@router.get("/sessions/{session_id}/report")
def download_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    pdf_bytes = generate_eligibility_report(session, messages, current_user)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=eligibility_report_{session_id}.pdf"},
    )
