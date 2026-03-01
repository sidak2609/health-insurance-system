import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import SessionLocal, create_tables
from app.db.models import Policy, PolicySection
from app.rag.ingest import build_vector_store


POLICIES = [
    {
        "name": "Basic Health Plan",
        "plan_type": "basic",
        "monthly_premium_base": 1500.00,
        "annual_deductible": 25000.00,
        "max_coverage_limit": 500000.00,
        "copay_percentage": 30.0,
        "coverage_details": json.dumps([
            "Emergency room visits",
            "Hospital stays (general ward)",
            "Primary care physician visits",
            "Generic prescription medications",
            "Preventive care and screenings",
            "Basic laboratory tests",
            "Ambulance services",
        ]),
        "exclusions": json.dumps([
            "Dental care",
            "Vision care",
            "Cosmetic surgery",
            "Fertility treatments",
            "Experimental treatments",
            "Ayurvedic and homeopathic treatments",
            "Hearing aids",
        ]),
        "age_min": 18,
        "age_max": 65,
        "smoker_surcharge_pct": 25.0,
        "bmi_surcharge_pct": 15.0,
        "pre_existing_waiting_months": 12,
        "sections": [
            {
                "section_title": "Eligibility Requirements",
                "section_number": 1,
                "keywords": json.dumps(["eligibility", "age", "qualify", "enrollment"]),
                "section_content": """Basic Health Plan - Eligibility Requirements

To be eligible for the Basic Health Plan, applicants must meet the following criteria:
- Age: Must be between 18 and 65 years old at the time of enrollment.
- Residency: Must be a resident of India with valid Aadhaar or PAN identification.
- No active enrollment in a competing plan from the same provider.

Pre-existing conditions are accepted, but subject to a 12-month waiting period before coverage begins for those conditions. During this waiting period, claims related to pre-existing conditions will not be reimbursed.

Smokers are accepted but will incur a 25% surcharge on the base monthly premium. BMI over 30 will incur a 15% surcharge. These surcharges reflect the increased health risk and cost associated with these factors.

Enrollment is available during the annual open enrollment period or within 30 days of a qualifying life event (marriage, birth of a child, loss of other coverage). All policies are regulated under IRDAI guidelines.""",
            },
            {
                "section_title": "Covered Services",
                "section_number": 2,
                "keywords": json.dumps(["coverage", "covered", "services", "benefits", "included"]),
                "section_content": """Basic Health Plan - Covered Services

The Basic Health Plan provides coverage for the following essential health services:

1. Emergency Room Visits: Full coverage after deductible and copay. Includes emergency physician fees, facility charges, and emergency medications.

2. Hospital Stays: General ward accommodation for medically necessary inpatient stays. Covers room and board, nursing care, and in-hospital medications.

3. Primary Care Physician Visits: Up to 12 visits per year for routine health concerns, follow-up appointments, and health monitoring.

4. Generic Prescription Medications: Coverage for DCGI-approved generic medications. Brand-name drugs are not covered under this plan.

5. Preventive Care: Annual physical examinations, recommended immunizations, cancer screenings (mammograms, colonoscopies as age-appropriate), and basic health risk assessments at no additional cost.

6. Basic Laboratory Tests: Standard blood work, urinalysis, and basic diagnostic tests when ordered by a covered physician.

7. Ambulance Services: Emergency ground ambulance transportation to the nearest appropriate facility.""",
            },
            {
                "section_title": "Exclusions and Limitations",
                "section_number": 3,
                "keywords": json.dumps(["exclusion", "not covered", "limitation", "excluded"]),
                "section_content": """Basic Health Plan - Exclusions and Limitations

The following services and treatments are NOT covered under the Basic Health Plan:

- Dental Care: All dental services including routine cleanings, fillings, extractions, and orthodontics.
- Vision Care: Eye examinations, prescription eyewear, contact lenses, and corrective eye surgery.
- Cosmetic Surgery: Any surgical procedure performed primarily to improve physical appearance.
- Fertility Treatments: In vitro fertilization (IVF), artificial insemination, fertility drugs, and related procedures.
- Experimental Treatments: Any treatment, procedure, or medication not yet approved by the DCGI or considered experimental.
- Ayurvedic and Homeopathic Treatments: Alternative medicine therapies and related treatments.
- Hearing Aids: Hearing devices and related fitting services.
- Mental Health Services: Psychiatric care, counseling, and therapy sessions are not included in the Basic plan.
- Physical Therapy: Rehabilitation services beyond initial post-surgical recovery.
- Brand-Name Medications: Only generic equivalents are covered.

Annual coverage is limited to ₹5,00,000. Any costs exceeding this amount are the responsibility of the insured. The annual deductible of ₹25,000 must be met before coverage begins. After the deductible, the plan pays 70% of covered services (30% copay).""",
            },
            {
                "section_title": "Claims Process",
                "section_number": 4,
                "keywords": json.dumps(["claim", "submit", "reimbursement", "file", "process"]),
                "section_content": """Basic Health Plan - Claims Process

To file a claim under the Basic Health Plan:

1. Submit your claim within 90 days of receiving the medical service.
2. Include all required documentation: itemized bill, physician's statement, and proof of payment.
3. Claims can be submitted through the online portal or by mail.
4. Processing time is typically 15-30 business days.
5. Approved claims will be reimbursed via NEFT/IMPS bank transfer or cheque.
6. If a claim is denied, you have 60 days to file an appeal with supporting documentation.

Claims are reviewed based on medical necessity and policy coverage terms. The copay percentage (30%) applies to all covered services after the annual deductible (₹25,000) has been met.""",
            },
        ],
    },
    {
        "name": "Standard Health Plan",
        "plan_type": "standard",
        "monthly_premium_base": 3000.00,
        "annual_deductible": 15000.00,
        "max_coverage_limit": 1500000.00,
        "copay_percentage": 20.0,
        "coverage_details": json.dumps([
            "Emergency room visits",
            "Hospital stays (semi-private room)",
            "Primary care physician visits",
            "Specialist consultations",
            "Generic and brand-name prescription medications",
            "Preventive care and screenings",
            "Diagnostic imaging (X-ray, MRI, CT scan)",
            "Mental health services",
            "Physical therapy (up to 30 sessions/year)",
            "Laboratory tests (comprehensive)",
            "Ambulance services",
        ]),
        "exclusions": json.dumps([
            "Cosmetic surgery",
            "Fertility treatments",
            "Experimental treatments",
            "Dental implants",
            "Vision correction surgery (LASIK)",
        ]),
        "age_min": 18,
        "age_max": 70,
        "smoker_surcharge_pct": 20.0,
        "bmi_surcharge_pct": 10.0,
        "pre_existing_waiting_months": 6,
        "sections": [
            {
                "section_title": "Eligibility Requirements",
                "section_number": 1,
                "keywords": json.dumps(["eligibility", "age", "qualify", "enrollment"]),
                "section_content": """Standard Health Plan - Eligibility Requirements

The Standard Health Plan offers broader coverage with the following eligibility criteria:
- Age: Must be between 18 and 70 years old at the time of enrollment.
- Residency: Must be a resident of India with valid Aadhaar or PAN identification.

Pre-existing conditions are accepted with a reduced 6-month waiting period. This is significantly shorter than the Basic plan's 12-month waiting period, providing faster access to full coverage.

Smokers will incur a 20% surcharge on the base premium. BMI over 30 will incur a 10% surcharge. These surcharges are lower than the Basic plan, reflecting the broader risk pool of the Standard plan.

The Standard plan is ideal for individuals and families who want comprehensive coverage including specialist care, mental health services, and brand-name medications. All policies are regulated under IRDAI guidelines.""",
            },
            {
                "section_title": "Covered Services",
                "section_number": 2,
                "keywords": json.dumps(["coverage", "covered", "services", "benefits", "included"]),
                "section_content": """Standard Health Plan - Covered Services

The Standard Health Plan includes all Basic plan services plus additional coverage:

1. Emergency Room Visits: Full coverage after deductible and copay, including follow-up care.

2. Hospital Stays: Semi-private room accommodation for medically necessary stays, including intensive care when required.

3. Primary Care & Specialist Visits: Unlimited primary care visits and up to 20 specialist consultations per year, including referral-based specialty care.

4. Prescription Medications: Both generic and brand-name medications are covered. Formulary restrictions may apply to certain specialty drugs. All medications must be DCGI-approved.

5. Mental Health Services: Outpatient therapy sessions (up to 24 per year), psychiatric consultations, and crisis intervention services. Covers conditions including depression, anxiety, PTSD, and other diagnosed mental health conditions.

6. Physical Therapy: Up to 30 sessions per year for rehabilitation following injury, surgery, or for chronic condition management.

7. Diagnostic Imaging: X-rays, MRI scans, CT scans, ultrasounds, and other advanced imaging when ordered by a covered physician.

8. Preventive Care: Comprehensive preventive services including annual physicals, immunizations, health screenings, and wellness programs at no additional cost.

9. Laboratory Tests: Full range of diagnostic laboratory tests including blood panels, pathology, and specialized testing.""",
            },
            {
                "section_title": "Exclusions and Limitations",
                "section_number": 3,
                "keywords": json.dumps(["exclusion", "not covered", "limitation", "excluded"]),
                "section_content": """Standard Health Plan - Exclusions and Limitations

The following are NOT covered under the Standard Health Plan:

- Cosmetic Surgery: Procedures performed for aesthetic purposes rather than medical necessity.
- Fertility Treatments: IVF, artificial insemination, and related reproductive technologies.
- Experimental Treatments: Non-DCGI-approved therapies and clinical trial treatments.
- Dental Implants: While basic dental is partially covered for emergency extractions, dental implants are excluded.
- Vision Correction Surgery: LASIK and similar elective vision correction procedures.
- Long-term Custodial Care: Nursing home stays not related to acute medical treatment.

Annual coverage limit: ₹15,00,000. Annual deductible: ₹15,000. After deductible, the plan pays 80% of covered services (20% copay). Mental health services have a separate annual limit of 24 outpatient sessions.""",
            },
        ],
    },
    {
        "name": "Premium Health Plan",
        "plan_type": "premium",
        "monthly_premium_base": 5500.00,
        "annual_deductible": 5000.00,
        "max_coverage_limit": 5000000.00,
        "copay_percentage": 10.0,
        "coverage_details": json.dumps([
            "Emergency room visits",
            "Hospital stays (private room, including ICU)",
            "Primary care physician visits (unlimited)",
            "Specialist consultations (unlimited)",
            "Generic and brand-name prescription medications",
            "Specialty prescription medications",
            "Preventive care and comprehensive screenings",
            "Diagnostic imaging (all types)",
            "Mental health services (unlimited outpatient)",
            "Physical therapy (unlimited sessions)",
            "Dental care (basic and major)",
            "Vision care (exams and corrective lenses)",
            "Maternity and newborn care",
            "Rehabilitation services",
            "Laboratory tests (all types)",
            "Ambulance and air medical transport",
            "Home health care services",
        ]),
        "exclusions": json.dumps([
            "Cosmetic surgery (non-reconstructive)",
            "Experimental treatments not in clinical trials",
            "Weight loss surgery (unless medically necessary)",
        ]),
        "age_min": 0,
        "age_max": 75,
        "smoker_surcharge_pct": 15.0,
        "bmi_surcharge_pct": 8.0,
        "pre_existing_waiting_months": 3,
        "sections": [
            {
                "section_title": "Eligibility Requirements",
                "section_number": 1,
                "keywords": json.dumps(["eligibility", "age", "qualify", "enrollment"]),
                "section_content": """Premium Health Plan - Eligibility Requirements

The Premium Health Plan provides the most comprehensive coverage available:
- Age: Available for all ages from 0 to 75 years old, making it suitable for families with children.
- Residency: Must be a resident of India with valid Aadhaar or PAN identification.

Pre-existing conditions are accepted with only a 3-month waiting period — the shortest waiting period among all our plans. This means you can access coverage for pre-existing conditions much sooner.

Smokers will incur a 15% surcharge on the base premium. BMI over 30 will incur an 8% surcharge. These are the lowest surcharges across all our plans.

The Premium plan is designed for individuals and families who want maximum coverage with minimal out-of-pocket costs. It includes dental, vision, maternity, and mental health coverage. All policies are regulated under IRDAI guidelines.""",
            },
            {
                "section_title": "Covered Services",
                "section_number": 2,
                "keywords": json.dumps(["coverage", "covered", "services", "benefits", "included"]),
                "section_content": """Premium Health Plan - Covered Services

The Premium Health Plan provides the most extensive coverage:

1. Emergency & Hospital: Full emergency room coverage, private room hospital stays including ICU, and air medical transport for emergencies.

2. Physician Visits: Unlimited primary care and specialist visits with no referral required for specialists.

3. Prescription Medications: Full coverage for generic, brand-name, and specialty prescription medications. Includes mail-order pharmacy options for maintenance medications. All medications must be DCGI-approved.

4. Mental Health: Unlimited outpatient therapy sessions, psychiatric care, substance abuse treatment, and crisis intervention. No separate annual limit on mental health services.

5. Physical Therapy & Rehabilitation: Unlimited physical therapy sessions, occupational therapy, speech therapy, and comprehensive rehabilitation programs.

6. Dental Care: Covers preventive dental (cleanings, X-rays), basic procedures (fillings, extractions), and major dental work (crowns, bridges). Annual dental maximum: ₹50,000.

7. Vision Care: Annual eye examinations, prescription eyewear (frames and lenses), and contact lenses. Vision benefit up to ₹10,000 annually.

8. Maternity & Newborn Care: Full prenatal care, delivery (normal and cesarean), postnatal care, and newborn care for the first 30 days. Includes lactation consulting and birthing classes.

9. Preventive Care: Comprehensive wellness programs, annual executive health screenings, genetic testing when recommended, and personalized health coaching.

10. Home Health Care: Skilled nursing visits, home health aide services, and medical equipment for home use when prescribed.""",
            },
            {
                "section_title": "Exclusions and Limitations",
                "section_number": 3,
                "keywords": json.dumps(["exclusion", "not covered", "limitation", "excluded"]),
                "section_content": """Premium Health Plan - Exclusions and Limitations

The Premium plan has minimal exclusions:

- Cosmetic Surgery: Non-reconstructive cosmetic procedures. Reconstructive surgery following accidents or medical conditions IS covered.
- Experimental Treatments: Treatments not approved by the DCGI and not part of registered clinical trials.
- Elective Weight Loss Surgery: Bariatric surgery unless deemed medically necessary by two independent physicians and BMI is over 40 (or over 35 with serious comorbidities).

Annual coverage limit: ₹50,00,000. Annual deductible: ₹5,000 (lowest available). After deductible, the plan pays 90% of covered services (10% copay — lowest available). Dental coverage has a separate annual maximum of ₹50,000. Vision coverage has a separate annual maximum of ₹10,000.

Out-of-pocket maximum: ₹50,000 per year per individual, ₹1,00,000 per family. Once the out-of-pocket maximum is reached, the plan covers 100% of remaining eligible expenses for the year.""",
            },
            {
                "section_title": "Claims Process",
                "section_number": 4,
                "keywords": json.dumps(["claim", "submit", "reimbursement", "file", "process"]),
                "section_content": """Premium Health Plan - Claims Process

The Premium plan offers an expedited claims process:

1. Submit claims within 180 days of service (extended from the standard 90 days).
2. Online portal submission with real-time tracking and status updates.
3. Priority processing: Claims are typically processed within 5-10 business days.
4. Cashless treatment at network hospitals (no upfront payment required).
5. 24/7 claims support helpline with dedicated case managers.
6. Extended appeal period of 90 days with complimentary medical review.

Premium plan members also have access to a concierge health service that can help coordinate care, find specialists, and manage complex treatment plans.""",
            },
        ],
    },
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        existing = db.query(Policy).count()
        if existing > 0:
            print(f"Database already has {existing} policies. Skipping seed.")
            print("Building/rebuilding FAISS vector store...")
            build_vector_store(db)
            return

        for policy_data in POLICIES:
            sections_data = policy_data.pop("sections")
            policy = Policy(**policy_data)
            db.add(policy)
            db.commit()
            db.refresh(policy)

            for section_data in sections_data:
                section = PolicySection(policy_id=policy.id, **section_data)
                db.add(section)

            db.commit()
            print(f"Created policy: {policy.name} with {len(sections_data)} sections")

        print("Building FAISS vector store...")
        build_vector_store(db)
        print("Seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
