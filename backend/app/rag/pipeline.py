import json

from sqlalchemy.orm import Session

from app.db.models import ChatSession, ChatMessage, Policy
from app.rag.ingest import get_vector_store
from app.rag.assessment import EligibilityAssessor
from app.models.schemas import ChatResponse, CitationItem


assessor = EligibilityAssessor()


def process_chat_message(
    db: Session,
    user_id: int,
    message: str,
    session_id: int = None,
    patient_details: dict = None,
) -> ChatResponse:
    # Get or create session
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        ).first()
        if not session:
            session = ChatSession(user_id=user_id, title=message[:50])
            db.add(session)
            db.commit()
            db.refresh(session)
    else:
        session = ChatSession(user_id=user_id, title=message[:50])
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=message,
    )
    db.add(user_msg)
    db.commit()

    # FAISS similarity search
    try:
        vector_store = get_vector_store()
        retrieved_docs = vector_store.similarity_search(message, k=6)
    except Exception:
        retrieved_docs = []

    # Classify intent
    intents = assessor.classify_intent(message)

    # Extract conditions mentioned
    mentioned_conditions = assessor.extract_condition_mentions(message)

    # Determine the best-matching policy from retrieved docs
    policy = None
    if retrieved_docs:
        policy_id = retrieved_docs[0].metadata.get("policy_id")
        if policy_id:
            policy = db.query(Policy).filter(Policy.id == policy_id).first()

    if not policy:
        # Fallback to first active policy
        policy = db.query(Policy).filter(Policy.is_active == True).first()

    if not policy:
        # No policies at all
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content="No policies are currently available. Please contact the insurer.",
            citations="[]",
            follow_up_questions="[]",
        )
        db.add(assistant_msg)
        db.commit()
        return ChatResponse(
            session_id=session.id,
            message="No policies are currently available. Please contact the insurer.",
            citations=[],
            follow_up_questions=[],
        )

    # Age check
    patient_age = patient_details.get("age") if patient_details else None
    age_check = assessor.check_age_eligibility(patient_age, policy) if patient_age else {}

    # Coverage check
    coverage_assessment = assessor.check_coverage(
        message, retrieved_docs, mentioned_conditions, policy
    )

    # Generate response
    response_text, follow_ups = assessor.generate_response(
        query=message,
        intents=intents,
        coverage_assessment=coverage_assessment,
        age_check=age_check,
        policy=policy,
        patient_details=patient_details,
    )

    # Build citations
    citations = []
    seen = set()
    for doc in retrieved_docs[:4]:
        meta = doc.metadata
        key = (meta.get("policy_name", ""), meta.get("section_title", ""))
        if key not in seen:
            seen.add(key)
            citations.append(CitationItem(
                policy_name=meta.get("policy_name", "Unknown"),
                section_title=meta.get("section_title", "Unknown"),
                section_number=meta.get("section_number", 0),
                excerpt=doc.page_content[:300],
            ))

    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_text,
        citations=json.dumps([c.model_dump() for c in citations]),
        follow_up_questions=json.dumps(follow_ups),
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        session_id=session.id,
        message=response_text,
        citations=citations,
        follow_up_questions=follow_ups,
    )
