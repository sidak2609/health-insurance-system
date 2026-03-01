"""
Seeds the entire database with:
- 3 policies + sections + FAISS index
- 2 patients + 1 insurer
- 8 claims (various statuses)
- Chat sessions with messages
- Notifications
- Audit logs
"""
import json
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import SessionLocal, create_tables, engine, Base
from app.db.models import (
    User, Policy, PolicySection, Claim, Notification,
    AuditLog, ChatSession, ChatMessage, Document,
)
from app.services.auth_service import hash_password
from app.services.risk_scoring import calculate_risk_score
from knowledge_base.seed_policies import POLICIES
from app.rag.ingest import build_vector_store


def seed_all():
    # Drop and recreate all tables for a clean start
    Base.metadata.drop_all(bind=engine)
    create_tables()
    db = SessionLocal()

    try:
        # ============================================================
        # 1. POLICIES + SECTIONS
        # ============================================================
        print("Seeding policies...")
        policy_objects = []
        for policy_data in POLICIES:
            sections_data = policy_data.pop("sections")
            policy = Policy(**policy_data)
            db.add(policy)
            db.commit()
            db.refresh(policy)
            policy_objects.append(policy)

            for section_data in sections_data:
                section = PolicySection(policy_id=policy.id, **section_data)
                db.add(section)
            db.commit()
            # Re-add sections key so POLICIES isn't mutated for reruns
            policy_data["sections"] = sections_data
            print(f"  Created: {policy.name}")

        basic, standard, premium = policy_objects

        # Build FAISS vector store
        print("Building FAISS vector store...")
        build_vector_store(db)

        # ============================================================
        # 2. USERS
        # ============================================================
        print("\nSeeding users...")

        patient1 = User(
            email="rajesh@patient.com",
            hashed_password=hash_password("password123"),
            full_name="Rajesh Kumar",
            role="patient",
            age=35,
            bmi=26.2,
            is_smoker=False,
            pre_existing_conditions=json.dumps(["diabetes", "hypertension"]),
            created_at=datetime.utcnow() - timedelta(days=45),
        )
        db.add(patient1)

        patient2 = User(
            email="priya@patient.com",
            hashed_password=hash_password("password123"),
            full_name="Priya Sharma",
            role="patient",
            age=28,
            bmi=22.1,
            is_smoker=True,
            pre_existing_conditions=json.dumps(["asthma"]),
            created_at=datetime.utcnow() - timedelta(days=30),
        )
        db.add(patient2)

        insurer1 = User(
            email="admin@insurer.com",
            hashed_password=hash_password("password123"),
            full_name="Dr. Amit Patel",
            role="insurer",
            company_name="Star Health Insurance",
            created_at=datetime.utcnow() - timedelta(days=90),
        )
        db.add(insurer1)

        db.commit()
        db.refresh(patient1)
        db.refresh(patient2)
        db.refresh(insurer1)
        print(f"  Patient: {patient1.email} / password123")
        print(f"  Patient: {patient2.email} / password123")
        print(f"  Insurer: {insurer1.email} / password123")

        # ============================================================
        # 3. CLAIMS
        # ============================================================
        print("\nSeeding claims...")

        claims_data = [
            # Rajesh's claims
            {
                "patient_id": patient1.id, "policy_id": standard.id,
                "claim_type": "hospitalization",
                "description": "Emergency room visit for chest pain at Apollo Hospital. ECG and blood work performed. Overnight observation.",
                "amount_claimed": 37500.00, "status": "approved",
                "amount_approved": 35000.00, "reviewer_id": insurer1.id,
                "created_at": datetime.utcnow() - timedelta(days=35),
            },
            {
                "patient_id": patient1.id, "policy_id": standard.id,
                "claim_type": "prescription",
                "description": "Monthly diabetes medication - Metformin 500mg and insulin supplies from MedPlus pharmacy.",
                "amount_claimed": 2500.00, "status": "approved",
                "amount_approved": 2500.00, "reviewer_id": insurer1.id,
                "created_at": datetime.utcnow() - timedelta(days=20),
            },
            {
                "patient_id": patient1.id, "policy_id": standard.id,
                "claim_type": "outpatient",
                "description": "Specialist consultation for diabetes management and HbA1c testing at Fortis Hospital.",
                "amount_claimed": 3000.00, "status": "pending",
                "created_at": datetime.utcnow() - timedelta(days=5),
            },
            {
                "patient_id": patient1.id, "policy_id": standard.id,
                "claim_type": "dental",
                "description": "Dental cleaning and cavity filling at Clove Dental clinic.",
                "amount_claimed": 5000.00, "status": "rejected",
                "reviewer_id": insurer1.id,
                "rejection_reason": "Dental services are not covered under the Standard Health Plan. Please consider upgrading to the Premium plan for dental coverage.",
                "created_at": datetime.utcnow() - timedelta(days=15),
            },
            # Priya's claims
            {
                "patient_id": patient2.id, "policy_id": basic.id,
                "claim_type": "outpatient",
                "description": "Primary care visit for asthma follow-up and spirometry test at Max Hospital.",
                "amount_claimed": 1800.00, "status": "approved",
                "amount_approved": 1800.00, "reviewer_id": insurer1.id,
                "created_at": datetime.utcnow() - timedelta(days=25),
            },
            {
                "patient_id": patient2.id, "policy_id": basic.id,
                "claim_type": "prescription",
                "description": "Asthalin inhaler and montelukast prescription refill from Netmeds pharmacy.",
                "amount_claimed": 1200.00, "status": "approved",
                "amount_approved": 1200.00, "reviewer_id": insurer1.id,
                "created_at": datetime.utcnow() - timedelta(days=18),
            },
            {
                "patient_id": patient2.id, "policy_id": premium.id,
                "claim_type": "hospitalization",
                "description": "Severe asthma attack requiring 3-day hospitalization with nebulizer treatment at AIIMS.",
                "amount_claimed": 100000.00, "status": "under_review",
                "created_at": datetime.utcnow() - timedelta(days=3),
            },
            {
                "patient_id": patient2.id, "policy_id": basic.id,
                "claim_type": "vision",
                "description": "Annual eye exam and prescription glasses from Lenskart.",
                "amount_claimed": 3200.00, "status": "rejected",
                "reviewer_id": insurer1.id,
                "rejection_reason": "Vision care is excluded from the Basic Health Plan.",
                "created_at": datetime.utcnow() - timedelta(days=10),
            },
        ]

        for cd in claims_data:
            patient = db.query(User).filter(User.id == cd["patient_id"]).first()
            policy = db.query(Policy).filter(Policy.id == cd["policy_id"]).first()
            risk_score, risk_level = calculate_risk_score(
                age=patient.age, bmi=patient.bmi,
                is_smoker=patient.is_smoker,
                conditions=patient.get_conditions(),
                claim_amount=cd["amount_claimed"],
                policy_max=policy.max_coverage_limit,
            )
            claim = Claim(
                risk_score=risk_score, risk_level=risk_level, **cd,
            )
            db.add(claim)
        db.commit()
        print(f"  Created {len(claims_data)} claims")

        # ============================================================
        # 4. CHAT SESSIONS + MESSAGES
        # ============================================================
        print("\nSeeding chat sessions...")

        # Rajesh's chat session
        session1 = ChatSession(
            user_id=patient1.id,
            title="Eligibility for Standard Plan",
            created_at=datetime.utcnow() - timedelta(days=40),
        )
        db.add(session1)
        db.commit()
        db.refresh(session1)

        msgs1 = [
            ChatMessage(
                session_id=session1.id, role="user",
                content="Am I eligible for the Standard Health Plan? I'm 35 with diabetes and hypertension.",
                created_at=datetime.utcnow() - timedelta(days=40),
            ),
            ChatMessage(
                session_id=session1.id, role="assistant",
                content="Based on your query about **Standard Health Plan** (Standard Plan):\n\n**Age Eligibility:** You meet the age requirement (18-70 years) for Standard Health Plan.\n\n**Note:** You have listed pre-existing conditions: diabetes, hypertension. A 6-month waiting period may apply.\n\n**Plan Overview:**\n- Monthly Premium: \u20b93,000.00\n- Deductible: \u20b915,000\n- Max Coverage: \u20b915,00,000\n- Copay: 20%\n\n**Covered Services:** Emergency room visits, Hospital stays, Specialist consultations, Mental health services, Physical therapy",
                citations=json.dumps([
                    {"policy_name": "Standard Health Plan", "section_title": "Eligibility Requirements", "section_number": 1, "excerpt": "The Standard Health Plan offers broader coverage with age requirement 18-70 years..."},
                    {"policy_name": "Standard Health Plan", "section_title": "Covered Services", "section_number": 2, "excerpt": "Includes all Basic plan services plus specialist consultations, mental health, physical therapy..."},
                ]),
                follow_up_questions=json.dumps([
                    "What specific conditions would you like to check coverage for?",
                    "Would you like to see the premium breakdown for this plan?",
                    "Would you like to compare this with other available plans?",
                ]),
                created_at=datetime.utcnow() - timedelta(days=40),
            ),
            ChatMessage(
                session_id=session1.id, role="user",
                content="Is diabetes treatment covered?",
                created_at=datetime.utcnow() - timedelta(days=40),
            ),
            ChatMessage(
                session_id=session1.id, role="assistant",
                content="Based on your query about **Standard Health Plan** (Standard Plan):\n\n**Coverage Information:**\nDiabetes management is covered under the Standard Health Plan, including:\n- Specialist consultations (endocrinologist)\n- Prescription medications (both generic and brand-name)\n- Laboratory tests (HbA1c, blood glucose monitoring)\n- Up to 20 specialist visits per year\n\n**Note:** Since diabetes is a pre-existing condition, there is a **6-month waiting period** before coverage begins for diabetes-related claims. After the waiting period, full coverage applies subject to the plan's deductible (\u20b915,000) and copay (20%).",
                citations=json.dumps([
                    {"policy_name": "Standard Health Plan", "section_title": "Covered Services", "section_number": 2, "excerpt": "Prescription Medications: Both generic and brand-name medications are covered..."},
                    {"policy_name": "Standard Health Plan", "section_title": "Exclusions and Limitations", "section_number": 3, "excerpt": "Annual coverage limit: \u20b915,00,000. After deductible, the plan pays 80%..."},
                ]),
                follow_up_questions=json.dumps([
                    "Would you like to know about the claims process?",
                    "Would you like to compare diabetes coverage across all plans?",
                ]),
                created_at=datetime.utcnow() - timedelta(days=40),
            ),
        ]
        for m in msgs1:
            db.add(m)

        # Priya's chat session
        session2 = ChatSession(
            user_id=patient2.id,
            title="Coverage for asthma treatment",
            created_at=datetime.utcnow() - timedelta(days=28),
        )
        db.add(session2)
        db.commit()
        db.refresh(session2)

        msgs2 = [
            ChatMessage(
                session_id=session2.id, role="user",
                content="Does the Basic plan cover asthma medication and inhalers?",
                created_at=datetime.utcnow() - timedelta(days=28),
            ),
            ChatMessage(
                session_id=session2.id, role="assistant",
                content="Based on your query about **Basic Health Plan** (Basic Plan):\n\n**Coverage for Asthma:**\nThe Basic Health Plan covers generic prescription medications, which includes generic asthma inhalers like Asthalin. However, brand-name inhalers are **not covered** under the Basic plan.\n\n**Covered:**\n- Generic prescription medications (Asthalin generic inhalers)\n- Primary care physician visits (up to 12/year)\n- Emergency room visits\n- Basic laboratory tests\n\n**Not Covered:**\n- Brand-name medications\n- Specialist consultations (pulmonologist)\n\n**Note:** As a smoker, a 25% surcharge applies to your premium. Consider the Standard plan for broader coverage including specialist visits.",
                citations=json.dumps([
                    {"policy_name": "Basic Health Plan", "section_title": "Covered Services", "section_number": 2, "excerpt": "Generic Prescription Medications: Coverage for DCGI-approved generic medications..."},
                    {"policy_name": "Basic Health Plan", "section_title": "Exclusions and Limitations", "section_number": 3, "excerpt": "Brand-Name Medications: Only generic equivalents are covered..."},
                ]),
                follow_up_questions=json.dumps([
                    "Would you like to compare the Basic and Standard plans?",
                    "Would you like a premium estimate for the Standard plan?",
                ]),
                created_at=datetime.utcnow() - timedelta(days=28),
            ),
        ]
        for m in msgs2:
            db.add(m)
        db.commit()
        print(f"  Created 2 chat sessions with {len(msgs1) + len(msgs2)} messages")

        # ============================================================
        # 5. NOTIFICATIONS
        # ============================================================
        print("\nSeeding notifications...")

        notifications = [
            # For insurer
            Notification(
                user_id=insurer1.id,
                title="New Claim Submitted",
                message="A new outpatient claim for \u20b93,000.00 has been submitted by Rajesh Kumar (Risk: medium).",
                notification_type="claim_submitted",
                is_read=False,
                related_entity_type="claim",
                related_entity_id=3,
                created_at=datetime.utcnow() - timedelta(days=5),
            ),
            Notification(
                user_id=insurer1.id,
                title="New Claim Submitted",
                message="A new hospitalization claim for \u20b91,00,000.00 has been submitted by Priya Sharma (Risk: medium).",
                notification_type="claim_submitted",
                is_read=False,
                related_entity_type="claim",
                related_entity_id=7,
                created_at=datetime.utcnow() - timedelta(days=3),
            ),
            Notification(
                user_id=insurer1.id,
                title="High-Value Claim Alert",
                message="Claim #7 exceeds \u20b950,000. Manual review recommended.",
                notification_type="claim_submitted",
                is_read=False,
                created_at=datetime.utcnow() - timedelta(days=3),
            ),
            # For patient1
            Notification(
                user_id=patient1.id,
                title="Claim Approved",
                message="Your hospitalization claim #1 has been approved. Approved amount: \u20b935,000.00",
                notification_type="claim_approved",
                is_read=True,
                related_entity_type="claim",
                related_entity_id=1,
                created_at=datetime.utcnow() - timedelta(days=33),
            ),
            Notification(
                user_id=patient1.id,
                title="Claim Approved",
                message="Your prescription claim #2 has been approved. Approved amount: \u20b92,500.00",
                notification_type="claim_approved",
                is_read=True,
                related_entity_type="claim",
                related_entity_id=2,
                created_at=datetime.utcnow() - timedelta(days=18),
            ),
            Notification(
                user_id=patient1.id,
                title="Claim Rejected",
                message="Your dental claim #4 has been rejected. Reason: Dental services are not covered under the Standard Health Plan.",
                notification_type="claim_rejected",
                is_read=False,
                related_entity_type="claim",
                related_entity_id=4,
                created_at=datetime.utcnow() - timedelta(days=14),
            ),
            # For patient2
            Notification(
                user_id=patient2.id,
                title="Claim Approved",
                message="Your outpatient claim #5 has been approved. Approved amount: \u20b91,800.00",
                notification_type="claim_approved",
                is_read=True,
                related_entity_type="claim",
                related_entity_id=5,
                created_at=datetime.utcnow() - timedelta(days=23),
            ),
            Notification(
                user_id=patient2.id,
                title="Claim Rejected",
                message="Your vision claim #8 has been rejected. Reason: Vision care is excluded from the Basic Health Plan.",
                notification_type="claim_rejected",
                is_read=False,
                related_entity_type="claim",
                related_entity_id=8,
                created_at=datetime.utcnow() - timedelta(days=9),
            ),
        ]
        for n in notifications:
            db.add(n)
        db.commit()
        print(f"  Created {len(notifications)} notifications")

        # ============================================================
        # 6. AUDIT LOGS
        # ============================================================
        print("\nSeeding audit logs...")

        audit_logs = [
            AuditLog(user_id=patient1.id, action="user_registered", entity_type="user", entity_id=patient1.id,
                     details=json.dumps({"role": "patient"}), created_at=datetime.utcnow() - timedelta(days=45)),
            AuditLog(user_id=patient2.id, action="user_registered", entity_type="user", entity_id=patient2.id,
                     details=json.dumps({"role": "patient"}), created_at=datetime.utcnow() - timedelta(days=30)),
            AuditLog(user_id=insurer1.id, action="user_registered", entity_type="user", entity_id=insurer1.id,
                     details=json.dumps({"role": "insurer"}), created_at=datetime.utcnow() - timedelta(days=90)),
            AuditLog(user_id=patient1.id, action="claim_submitted", entity_type="claim", entity_id=1,
                     details=json.dumps({"amount": 37500.0, "risk_level": "medium"}), created_at=datetime.utcnow() - timedelta(days=35)),
            AuditLog(user_id=insurer1.id, action="claim_approved", entity_type="claim", entity_id=1,
                     details=json.dumps({"amount_approved": 35000.0}), created_at=datetime.utcnow() - timedelta(days=33)),
            AuditLog(user_id=patient1.id, action="claim_submitted", entity_type="claim", entity_id=2,
                     details=json.dumps({"amount": 2500.0, "risk_level": "medium"}), created_at=datetime.utcnow() - timedelta(days=20)),
            AuditLog(user_id=insurer1.id, action="claim_approved", entity_type="claim", entity_id=2,
                     details=json.dumps({"amount_approved": 2500.0}), created_at=datetime.utcnow() - timedelta(days=18)),
            AuditLog(user_id=patient1.id, action="claim_submitted", entity_type="claim", entity_id=4,
                     details=json.dumps({"amount": 5000.0, "risk_level": "medium"}), created_at=datetime.utcnow() - timedelta(days=15)),
            AuditLog(user_id=insurer1.id, action="claim_rejected", entity_type="claim", entity_id=4,
                     details=json.dumps({"rejection_reason": "Dental not covered"}), created_at=datetime.utcnow() - timedelta(days=14)),
            AuditLog(user_id=patient2.id, action="claim_submitted", entity_type="claim", entity_id=5,
                     details=json.dumps({"amount": 1800.0, "risk_level": "low"}), created_at=datetime.utcnow() - timedelta(days=25)),
            AuditLog(user_id=insurer1.id, action="claim_approved", entity_type="claim", entity_id=5,
                     details=json.dumps({"amount_approved": 1800.0}), created_at=datetime.utcnow() - timedelta(days=23)),
            AuditLog(user_id=patient2.id, action="claim_submitted", entity_type="claim", entity_id=7,
                     details=json.dumps({"amount": 100000.0, "risk_level": "medium"}), created_at=datetime.utcnow() - timedelta(days=3)),
            AuditLog(user_id=insurer1.id, action="user_login", entity_type="user", entity_id=insurer1.id,
                     details=json.dumps({}), created_at=datetime.utcnow() - timedelta(days=1)),
            AuditLog(user_id=patient1.id, action="user_login", entity_type="user", entity_id=patient1.id,
                     details=json.dumps({}), created_at=datetime.utcnow() - timedelta(hours=6)),
        ]
        for a in audit_logs:
            db.add(a)
        db.commit()
        print(f"  Created {len(audit_logs)} audit log entries")

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 55)
        print("  DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 55)
        print(f"\n  Policies:       {db.query(Policy).count()}")
        print(f"  Policy Sections: {db.query(PolicySection).count()}")
        print(f"  Users:          {db.query(User).count()}")
        print(f"  Claims:         {db.query(Claim).count()}")
        print(f"  Chat Sessions:  {db.query(ChatSession).count()}")
        print(f"  Chat Messages:  {db.query(ChatMessage).count()}")
        print(f"  Notifications:  {db.query(Notification).count()}")
        print(f"  Audit Logs:     {db.query(AuditLog).count()}")
        print(f"\n  Login Credentials:")
        print(f"  ─────────────────────────────────────")
        print(f"  Patient:  rajesh@patient.com / password123")
        print(f"  Patient:  priya@patient.com  / password123")
        print(f"  Insurer:  admin@insurer.com  / password123")
        print(f"\n  Database: health_insurance.db")
        print("=" * 55)

    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
