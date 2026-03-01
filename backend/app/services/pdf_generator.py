import io
import json
from datetime import datetime

from fpdf import FPDF


def generate_eligibility_report(session, messages, user) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Eligibility Assessment Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
    pdf.ln(5)

    # Patient info
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Patient Information", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Name: {user.full_name}", ln=True)
    pdf.cell(0, 6, f"Email: {user.email}", ln=True)
    if user.age:
        pdf.cell(0, 6, f"Age: {user.age}", ln=True)
    if user.bmi:
        pdf.cell(0, 6, f"BMI: {user.bmi}", ln=True)
    pdf.cell(0, 6, f"Smoker: {'Yes' if user.is_smoker else 'No'}", ln=True)
    conditions = user.get_conditions()
    if conditions:
        pdf.cell(0, 6, f"Pre-existing Conditions: {', '.join(conditions)}", ln=True)
    pdf.ln(5)

    # Session info
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Chat Session: {session.title}", ln=True)
    pdf.ln(3)

    # Messages
    for msg in messages:
        role_label = "You" if msg.role == "user" else "Assessment"
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"{role_label}:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        # Handle long text with multi_cell
        pdf.multi_cell(0, 5, msg.content)

        # Citations
        try:
            citations = json.loads(msg.citations or "[]")
        except (json.JSONDecodeError, TypeError):
            citations = []

        if citations:
            pdf.set_font("Helvetica", "I", 8)
            for cit in citations:
                policy = cit.get("policy_name", "")
                section = cit.get("section_title", "")
                pdf.cell(0, 5, f"  Source: {policy} - {section}", ln=True)
        pdf.ln(3)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def generate_claim_report(claim, patient, policy) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Claim Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Claim Details", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Claim ID: {claim.id}", ln=True)
    pdf.cell(0, 6, f"Status: {claim.status}", ln=True)
    pdf.cell(0, 6, f"Type: {claim.claim_type}", ln=True)
    pdf.cell(0, 6, f"Amount Claimed: ${claim.amount_claimed:,.2f}", ln=True)
    if claim.amount_approved:
        pdf.cell(0, 6, f"Amount Approved: ${claim.amount_approved:,.2f}", ln=True)
    if claim.risk_score is not None:
        pdf.cell(0, 6, f"Risk Score: {claim.risk_score} ({claim.risk_level})", ln=True)
    if claim.rejection_reason:
        pdf.cell(0, 6, f"Rejection Reason: {claim.rejection_reason}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Patient Information", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Name: {patient.full_name}", ln=True)
    pdf.cell(0, 6, f"Policy: {policy.name}", ln=True)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
