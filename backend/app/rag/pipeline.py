import json
import os

from sqlalchemy.orm import Session

from app.db.models import ChatSession, ChatMessage, Policy, Claim
from app.rag.ingest import keyword_search
from app.rag.assessment import EligibilityAssessor, _calculate_personalized_premium
from app.models.schemas import ChatResponse, CitationItem

assessor = EligibilityAssessor()

# Lazy Anthropic client
_anthropic_client = None

def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                _anthropic_client = anthropic.Anthropic(api_key=api_key)
        except Exception:
            pass
    return _anthropic_client


def _build_system_prompt(patient_details: dict, best_policy, calc_premium: float, premium_notes: list, claims_context: list, policy_context: str) -> str:
    pd = patient_details or {}
    full_name = pd.get("full_name", "Patient")
    first_name = full_name.split()[0] if full_name else "Patient"
    age = pd.get("age")
    bmi = pd.get("bmi")
    is_smoker = pd.get("is_smoker", False)
    conditions = pd.get("conditions", [])

    claims_text = ""
    if claims_context:
        for c in claims_context[:5]:
            amt_approved = f", ₹{c['amount_approved']:,.2f} approved" if c.get("amount_approved") else ""
            claims_text += f"  - Claim #{c['id']} ({c['claim_type'].title()}): ₹{c['amount_claimed']:,.2f} claimed{amt_approved} — Status: {c['status'].upper()}\n"
    else:
        claims_text = "  No claims on record yet.\n"

    policy_section = ""
    if best_policy:
        surcharge_note = ""
        if premium_notes:
            surcharge_note = f" (adjusted for {', '.join(premium_notes)})"
        policy_section = f"""
ENROLLED POLICY: {best_policy.name} ({best_policy.plan_type.title()} Plan)
  - Your Personalized Monthly Premium: ₹{calc_premium:,.2f}{surcharge_note}
  - Base Monthly Premium: ₹{best_policy.monthly_premium_base:,.2f}
  - Annual Deductible: ₹{best_policy.annual_deductible:,.2f}
  - Max Coverage Limit: ₹{best_policy.max_coverage_limit:,.2f}
  - Copay: {best_policy.copay_percentage:.0f}%
  - Pre-existing Waiting Period: {best_policy.pre_existing_waiting_months} months
  - Smoker Surcharge: {best_policy.smoker_surcharge_pct:.0f}%
  - BMI Surcharge: {best_policy.bmi_surcharge_pct:.0f}%
"""
    else:
        policy_section = "\n  No active policy found.\n"

    conditions_text = ", ".join(conditions) if conditions else "None listed"

    return f"""You are a knowledgeable, empathetic AI insurance assistant for a health insurance platform called HealthInsure. Your job is to help patients understand their specific coverage, eligibility, premiums, claims, and benefits.

PATIENT PROFILE:
  - Name: {full_name}
  - Age: {age if age else "Not provided"}
  - BMI: {f"{bmi:.1f}" if bmi else "Not provided"}
  - Smoker: {"Yes" if is_smoker else "No"}
  - Pre-existing Conditions: {conditions_text}
{policy_section}
PATIENT'S RECENT CLAIMS:
{claims_text}
RELEVANT POLICY KNOWLEDGE BASE:
{policy_context if policy_context else "  No specific sections retrieved."}

INSTRUCTIONS:
- Address the patient by their first name ({first_name}) naturally in your response.
- Give direct, specific answers using their actual profile data (age, BMI, conditions, smoking status).
- When calculating premiums, always use their personalized amount (₹{calc_premium:,.2f}/month), not the base rate.
- For coverage questions, check the knowledge base sections above and give a clear yes/no answer with details.
- For pre-existing conditions ({conditions_text}), always mention the {best_policy.pre_existing_waiting_months if best_policy else 'applicable'}-month waiting period.
- If asked about claims, reference their actual claim history shown above.
- Use ₹ (Indian Rupee) for all amounts.
- Keep responses clear, concise, and friendly. Use bullet points for lists.
- If the question is outside insurance scope, acknowledge it and suggest contacting the insurer at support@healthinsure.in or calling 1800-XXX-XXXX.
- Never make up coverage details not supported by the policy sections above.
- At the end of your response, suggest 2-3 relevant follow-up questions the patient might want to ask, formatted as a JSON array on the last line like: FOLLOWUPS: ["question1", "question2", "question3"]"""


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
    db.add(ChatMessage(session_id=session.id, role="user", content=message))
    db.commit()

    # Fetch patient's recent claims
    claims_context = []
    try:
        recent_claims = (
            db.query(Claim)
            .filter(Claim.patient_id == user_id)
            .order_by(Claim.created_at.desc())
            .limit(10)
            .all()
        )
        claims_context = [
            {
                "id": c.id,
                "claim_type": c.claim_type,
                "amount_claimed": c.amount_claimed,
                "amount_approved": c.amount_approved,
                "status": c.status,
                "description": c.description,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in recent_claims
        ]
    except Exception:
        claims_context = []

    # Keyword search over policy sections (no ML models needed)
    retrieved_docs = []
    try:
        retrieved_docs = keyword_search(db, message, k=8)
    except Exception:
        retrieved_docs = []

    # Determine best-matching policy
    policy = None
    if retrieved_docs:
        policy_id = retrieved_docs[0].metadata.get("policy_id")
        if policy_id:
            policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        policy = db.query(Policy).filter(Policy.is_active == True).first()

    if not policy:
        no_policy_msg = "No active insurance policies found. Please contact your insurer."
        db.add(ChatMessage(
            session_id=session.id, role="assistant",
            content=no_policy_msg, citations="[]", follow_up_questions="[]"
        ))
        db.commit()
        return ChatResponse(session_id=session.id, message=no_policy_msg, citations=[], follow_up_questions=[])

    # Calculate personalized premium
    pd = patient_details or {}
    calc_premium, premium_notes = _calculate_personalized_premium(
        policy, pd.get("age"), pd.get("bmi"), pd.get("is_smoker", False)
    )

    # Build policy context from retrieved docs
    policy_context_parts = []
    for doc in retrieved_docs[:6]:
        meta = doc.metadata
        policy_context_parts.append(
            f"[{meta.get('policy_name', '')} — {meta.get('section_title', '')}]\n{doc.page_content}"
        )
    policy_context = "\n\n".join(policy_context_parts)

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

    # Try Claude API first
    anthropic_client = _get_anthropic_client()
    response_text = None
    follow_ups = []

    if anthropic_client:
        try:
            system_prompt = _build_system_prompt(
                patient_details, policy, calc_premium, premium_notes,
                claims_context, policy_context
            )
            api_response = anthropic_client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
                system=system_prompt,
                messages=[{"role": "user", "content": message}]
            )
            full_text = api_response.content[0].text

            # Extract follow-up questions from the last line
            if "FOLLOWUPS:" in full_text:
                parts = full_text.rsplit("FOLLOWUPS:", 1)
                response_text = parts[0].strip()
                try:
                    follow_ups = json.loads(parts[1].strip())
                    if not isinstance(follow_ups, list):
                        follow_ups = []
                except Exception:
                    follow_ups = []
            else:
                response_text = full_text.strip()

        except Exception as e:
            print(f"Claude API error: {e}")
            response_text = None

    # Fallback to rule-based if Claude unavailable
    if not response_text:
        intents = assessor.classify_intent(message)
        mentioned_conditions = assessor.extract_condition_mentions(message)
        patient_age = pd.get("age")
        age_check = assessor.check_age_eligibility(patient_age, policy) if patient_age else {}
        coverage_assessment = assessor.check_coverage(message, retrieved_docs, mentioned_conditions, policy)
        response_text, follow_ups = assessor.generate_response(
            query=message,
            intents=intents,
            coverage_assessment=coverage_assessment,
            age_check=age_check,
            policy=policy,
            patient_details=patient_details,
            claims_context=claims_context,
        )

    # Ensure follow-ups are sensible
    if not follow_ups:
        conditions = pd.get("conditions", [])
        follow_ups = [
            f"What is my personalized monthly premium?",
            f"Am I covered for {conditions[0]}?" if conditions else "What services are covered?",
            "How do I submit a claim?",
        ]

    # Save assistant message
    db.add(ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_text,
        citations=json.dumps([c.model_dump() for c in citations]),
        follow_up_questions=json.dumps(follow_ups[:4]),
    ))
    db.commit()

    return ChatResponse(
        session_id=session.id,
        message=response_text,
        citations=citations,
        follow_up_questions=follow_ups[:4],
    )
