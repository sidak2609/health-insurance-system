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
            "Primary care physician visits (up to 12/year)",
            "Generic prescription medications",
            "Preventive care and screenings",
            "Basic laboratory tests",
            "Ambulance services (ground)",
            "Post-surgical follow-up (up to 3 visits)",
            "Basic X-ray and ultrasound",
            "Vaccinations and immunizations",
        ]),
        "exclusions": json.dumps([
            "Dental care (routine and major)",
            "Vision care and corrective lenses",
            "Cosmetic surgery",
            "Fertility treatments and IVF",
            "Experimental treatments",
            "Ayurvedic, homeopathic, and naturopathic treatments",
            "Hearing aids",
            "Mental health and psychiatric care",
            "Physical therapy beyond post-surgical recovery",
            "Brand-name medications (generics only)",
            "Air ambulance",
            "Weight loss programs",
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
                "keywords": json.dumps(["eligibility", "age", "qualify", "enrollment", "who can join", "requirements"]),
                "section_content": """Basic Health Plan — Eligibility Requirements

WHO CAN ENROLL:
- Age: 18 to 65 years at the time of enrollment
- Must be a resident of India with valid Aadhaar or PAN
- Not currently enrolled in a competing plan from the same provider
- No active insurance fraud or misrepresentation history

PRE-EXISTING CONDITIONS:
All pre-existing conditions are accepted, but subject to a 12-month waiting period. During this period, claims directly related to pre-existing conditions will not be reimbursed. Conditions include but are not limited to: diabetes, hypertension, heart disease, asthma, COPD, thyroid disorders, arthritis, and kidney disease.

SURCHARGES:
- Smokers (current or within the last 12 months): 25% surcharge on base monthly premium
- BMI 30 or above: 15% surcharge on base monthly premium
- Both surcharges may apply simultaneously

ENROLLMENT WINDOWS:
- Annual open enrollment period (October 1 to November 30)
- Within 30 days of a qualifying life event: marriage, birth/adoption of a child, loss of other coverage, relocation
- New employees within 30 days of joining an employer group plan

DEPENDENTS:
The Basic plan does not cover dependents. Each family member must enroll separately.""",
            },
            {
                "section_title": "Covered Services and Benefits",
                "section_number": 2,
                "keywords": json.dumps(["coverage", "covered", "services", "benefits", "included", "what is covered", "hospitalization"]),
                "section_content": """Basic Health Plan — Covered Services and Benefits

EMERGENCY SERVICES:
- Full emergency room visits after deductible and 30% copay
- Emergency physician fees, facility charges, emergency medications
- Emergency stabilization and observation (up to 24 hours)
- Ground ambulance transport to nearest appropriate facility

HOSPITAL STAYS (INPATIENT):
- General ward accommodation for medically necessary stays
- Room and board, nursing care, in-hospital medications
- Surgeon and anesthesiologist fees for covered surgeries
- Post-operative care during the hospital stay
- ICU not covered; step-down unit covered for up to 48 hours

PRIMARY CARE:
- Up to 12 primary care physician visits per year
- Consultation fees, routine examinations
- Health risk assessments and basic screenings
- Referrals to specialists (specialist visits NOT covered)

PREVENTIVE CARE (No copay, no deductible):
- Annual physical examination (1 per year)
- Recommended immunizations and vaccinations
- Cancer screenings: mammogram (age 40+), Pap smear (age 21+), colonoscopy (age 45+)
- Blood pressure and cholesterol screenings
- Diabetes screening (annual, if risk factors present)

PRESCRIPTION MEDICATIONS:
- DCGI-approved generic medications only
- 30-day supply per prescription; up to 3 refills per medication annually
- Must be prescribed by a covered physician

DIAGNOSTIC TESTS:
- Basic blood work: CBC, lipid panel, blood glucose, liver function, kidney function
- Urinalysis, basic X-rays (chest, extremities), ultrasound (abdominal, pelvic)""",
            },
            {
                "section_title": "Exclusions and Limitations",
                "section_number": 3,
                "keywords": json.dumps(["exclusion", "not covered", "limitation", "excluded", "what is not covered", "denied"]),
                "section_content": """Basic Health Plan — Exclusions and Limitations

COMPLETELY EXCLUDED (no coverage under any circumstances):
- All dental care: cleanings, fillings, extractions, root canals, crowns, orthodontics, dentures
- All vision care: eye exams, glasses, contact lenses, LASIK
- Mental health and psychiatric services: therapy, counseling, psychiatry, inpatient psychiatric stays
- Cosmetic and aesthetic procedures: rhinoplasty, liposuction, facelifts, breast augmentation
- Fertility treatments: IVF, IUI, egg freezing, fertility drugs, sperm banking
- Experimental and unproven treatments: any therapy not approved by DCGI
- Alternative medicine: Ayurveda, homeopathy, naturopathy, Unani, Siddha
- Hearing aids and cochlear implants
- Weight loss programs, bariatric surgery, diet medications
- Long-term care and nursing home stays

ANNUAL LIMITS:
- Total coverage: Rs 5,00,000 per year (all claims combined)
- Primary care visits: 12 per year
- Prescription refills: 3 per medication per year
- Ambulance: 2 emergency calls per year

COST SHARING:
- Annual deductible: Rs 25,000 (must be paid before coverage begins)
- Copay after deductible: 30% of covered services
- Example: Rs 1,00,000 hospital bill — you pay Rs 25,000 deductible + Rs 22,500 copay (30% of Rs 75,000) = Rs 47,500 out-of-pocket

WAITING PERIODS:
- Pre-existing conditions: 12-month waiting period
- Accidents and emergencies: covered from Day 1, no waiting period""",
            },
            {
                "section_title": "Claims Filing Process",
                "section_number": 4,
                "keywords": json.dumps(["claim", "submit", "reimbursement", "file", "process", "how to claim", "paperwork", "documents required"]),
                "section_content": """Basic Health Plan — Claims Filing Process

HOW TO SUBMIT A CLAIM:
1. Log into the HealthInsure patient portal at healthinsure.in
2. Click Submit New Claim under the Claims section
3. Select your claim type: Hospitalization, Outpatient, Prescription, Emergency
4. Upload required documents (list below)
5. Submit and note your claim reference number

REQUIRED DOCUMENTS:
- Itemized hospital or clinic bill (not just a summary)
- Discharge summary (for hospitalizations)
- Doctor's prescription (for medications)
- Lab reports and imaging reports (for diagnostics)
- Proof of payment (receipt or bank statement)
- Your policy number and patient ID

TIME LIMITS:
- Submit within 90 days of receiving the medical service
- Pre-authorization required before any planned hospitalization
- Emergency claims: notify us within 24 hours of emergency admission

PROCESSING TIME:
- Standard claims: 15 to 30 business days
- Emergency claims: 5 to 10 business days (priority processing)
- Payment via NEFT/IMPS to registered bank account within 7 days of approval

CASHLESS TREATMENT (Network Hospitals):
- Show your HealthInsure card at any network hospital
- Hospital bills insurer directly; you pay only deductible and copay
- Pre-authorization required for planned admissions

CLAIM DENIAL AND APPEALS:
- If denied, you will receive a written explanation
- File an appeal within 60 days of denial date
- Submit additional medical documentation to support your appeal
- Contact: claims@healthinsure.in or 1800-XXX-2222""",
            },
            {
                "section_title": "Pre-existing Conditions Policy",
                "section_number": 5,
                "keywords": json.dumps(["pre-existing", "waiting period", "diabetes", "hypertension", "heart disease", "asthma", "prior condition", "existing condition"]),
                "section_content": """Basic Health Plan — Pre-existing Conditions Policy

DEFINITION OF PRE-EXISTING CONDITION:
Any illness, injury, or medical condition for which symptoms existed, diagnosis was made, or treatment was received within 48 months prior to the policy start date.

COMMON PRE-EXISTING CONDITIONS (12-month waiting period applies):
- Diabetes (Type 1 and Type 2): includes insulin, metformin, and diabetic complications
- Hypertension (high blood pressure): includes hypertension medications and related cardiac monitoring
- Asthma and COPD: includes inhalers, nebulizers, and respiratory medications
- Heart disease: includes angina, prior heart attacks, arrhythmias
- Kidney disease: includes dialysis, CKD management
- Liver disease: includes hepatitis treatment, cirrhosis management
- Thyroid disorders: includes hypothyroidism and hyperthyroidism medications
- Arthritis: includes rheumatoid and osteoarthritis treatment
- Epilepsy: includes anti-epileptic medications
- Cancer (history of): coverage begins after 12 months, experimental treatments excluded

WHAT HAPPENS DURING THE WAITING PERIOD:
- Claims directly related to the pre-existing condition are denied
- Unrelated medical care (e.g., accident, unrelated illness) is covered from day 1
- Emergency care for any condition (including pre-existing) is covered from day 1

AFTER THE WAITING PERIOD:
- Full coverage for the pre-existing condition as per plan benefits
- No additional premiums or restrictions specifically for the condition

DECLARATION REQUIREMENT:
- All pre-existing conditions must be disclosed at enrollment
- Failure to disclose may result in claim denial and policy cancellation""",
            },
            {
                "section_title": "Emergency Coverage and Hospitalization Guide",
                "section_number": 6,
                "keywords": json.dumps(["emergency", "hospitalization", "accident", "ICU", "surgery", "urgent care", "ambulance", "ER"]),
                "section_content": """Basic Health Plan — Emergency Coverage and Hospitalization Guide

WHAT COUNTS AS AN EMERGENCY:
- Sudden acute illness with risk to life
- Accidental injury requiring immediate treatment
- Severe chest pain, breathing difficulty, stroke symptoms
- High fever with seizures in children
- Severe allergic reactions (anaphylaxis)
- Major trauma from accidents

WHAT TO DO IN AN EMERGENCY:
1. Call 108 (national ambulance) or go directly to the nearest hospital
2. Show your HealthInsure card at the emergency registration desk
3. Notify HealthInsure within 24 hours: call 1800-XXX-0000 (24/7 helpline)
4. Ask the hospital to initiate a cashless claim if they are a network hospital

EMERGENCY COVERAGE INCLUDES:
- Emergency room facility fees and emergency physician fees
- Emergency surgery if required
- Emergency medications administered during the visit
- Diagnostic tests ordered during the emergency (X-ray, blood work, ECG)
- Observation stays up to 24 hours
- Ground ambulance transport

NOT COVERED IN EMERGENCY:
- Air ambulance (not covered under Basic plan)
- Follow-up non-emergency visits after the initial emergency
- Prescription medications to take home after discharge

ACCIDENT COVERAGE:
- Accidents are covered from Day 1 with no waiting period
- Road traffic accidents, workplace injuries, falls, burns
- Includes fractures, lacerations, head injuries
- Surgery for accident-related injuries is covered""",
            },
            {
                "section_title": "Prescription Drug Coverage",
                "section_number": 7,
                "keywords": json.dumps(["medication", "prescription", "drugs", "pharmacy", "generic", "formulary", "medicine"]),
                "section_content": """Basic Health Plan — Prescription Drug Coverage

COVERED MEDICATIONS:
Only DCGI-approved generic medications are covered under the Basic plan. Brand-name drugs are not covered.

HOW TO USE YOUR PRESCRIPTION BENEFIT:
1. Get a prescription from a covered primary care physician
2. Fill at any empanelled pharmacy (list available at healthinsure.in/pharmacies)
3. Show your HealthInsure card and pay the 30% copay on drug cost
4. Deductible must be met before copay applies

COMMON COVERED GENERIC MEDICATIONS:
- Diabetes: Metformin, Glipizide, Glimepiride
- Hypertension: Amlodipine, Atenolol, Losartan, Lisinopril
- Asthma: Salbutamol inhaler, Beclomethasone inhaler, Montelukast
- Thyroid: Levothyroxine
- Infections: Amoxicillin, Azithromycin, Ciprofloxacin, Metronidazole
- Pain: Paracetamol, Ibuprofen, Diclofenac
- Gastrointestinal: Omeprazole, Pantoprazole, Domperidone

SUPPLY LIMITS:
- 30-day supply per prescription
- Maximum 3 refills per medication per year (4 fills total)
- Controlled substances require special authorization

NOT COVERED:
- Brand-name medications
- Specialty biologics and injectables
- Weight loss medications
- Vitamins and supplements (unless prescribed for deficiency)
- Medications for excluded conditions (dental, vision, mental health)""",
            },
            {
                "section_title": "Network Hospitals and Providers",
                "section_number": 8,
                "keywords": json.dumps(["network", "hospital", "doctor", "provider", "cashless", "empanelled", "list", "which hospital", "where to go"]),
                "section_content": """Basic Health Plan — Network Hospitals and Providers

CASHLESS TREATMENT NETWORK:
HealthInsure has a network of 2,500+ empanelled hospitals across India where you can receive cashless treatment.

HOW TO FIND A NETWORK HOSPITAL:
- Visit healthinsure.in/find-hospital
- Call 1800-XXX-4444 (hospital locator helpline)
- Use the HealthInsure mobile app, Hospital Finder section

MAJOR CITIES SAMPLE NETWORK HOSPITALS:
- Mumbai: Kokilaben Dhirubhai Ambani Hospital, Lilavati Hospital, Hinduja Hospital
- Delhi/NCR: Apollo Hospital, Max Super Speciality, Fortis Healthcare
- Bangalore: Manipal Hospital, Narayana Health, Apollo BGS
- Chennai: Apollo Hospitals Chennai, MIOT International
- Hyderabad: Apollo Hospitals Jubilee Hills, CARE Hospitals, Yashoda Hospital

NON-NETWORK HOSPITALS:
- Treatment at non-network hospitals requires you to pay upfront and then claim reimbursement
- Same coverage terms apply; processing takes 15 to 30 business days
- Keep all original bills, receipts, and discharge summaries

PRE-AUTHORIZATION FOR PLANNED HOSPITALIZATION:
1. Call 1800-XXX-1111 at least 48 hours before planned admission
2. Provide: hospital name, diagnosis, planned procedure, expected dates
3. Receive pre-authorization reference number
4. Share number with hospital billing department
5. For emergencies: authorization obtained post-admission within 24 hours""",
            },
            {
                "section_title": "Frequently Asked Questions",
                "section_number": 9,
                "keywords": json.dumps(["FAQ", "questions", "how", "when", "what happens", "can I", "help", "common questions"]),
                "section_content": """Basic Health Plan — Frequently Asked Questions

Q: When does my coverage start?
A: Coverage begins on the 1st of the month following your enrollment date. Pre-existing condition coverage starts after the 12-month waiting period.

Q: What happens if I am hospitalized for a pre-existing condition during the waiting period?
A: Emergency care is covered from Day 1, even for pre-existing conditions. Planned hospitalizations for pre-existing conditions during the waiting period will not be covered.

Q: Can I add my spouse or children to the Basic plan?
A: No. The Basic plan is individual coverage only. Each family member must enroll separately.

Q: Does the 30% copay apply to preventive care?
A: No. Preventive care services are covered at 100% with no deductible and no copay.

Q: What if my doctor prescribes a brand-name drug?
A: Ask your doctor if a generic equivalent is available. If not, you will need to pay the full cost of the brand-name drug out-of-pocket.

Q: I was in a car accident. Am I covered?
A: Yes. Accidents are covered from Day 1 with no waiting period. Emergency and hospitalization costs will be covered after your deductible and copay.

Q: My claim was denied. What can I do?
A: File an appeal within 60 days. Submit the denial letter, additional medical records, and a letter from your doctor explaining the medical necessity.

Q: How do I know which hospital is in-network?
A: Visit healthinsure.in/find-hospital or call 1800-XXX-4444.

Q: Can I see a specialist?
A: Specialist visits are not covered under the Basic plan. You can self-pay for specialist care. Consider upgrading to Standard or Premium plan for specialist coverage.

Q: What is the maximum I will pay out-of-pocket in a year?
A: Annual deductible (Rs 25,000) plus 30% copay on all covered services up to the Rs 5,00,000 coverage limit.

Q: How do I update my health information after quitting smoking?
A: Update your profile at healthinsure.in/profile or call 1800-XXX-5555. Surcharge adjustments apply at the next renewal date after verification (smoking cessation requires 12 months tobacco-free).""",
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
            "Emergency room visits (full coverage)",
            "Hospital stays (semi-private room including ICU)",
            "Primary care physician visits (unlimited)",
            "Specialist consultations (up to 20/year)",
            "Generic and brand-name prescription medications",
            "Preventive care and comprehensive screenings",
            "Diagnostic imaging (X-ray, MRI, CT scan, ultrasound)",
            "Mental health services (24 outpatient sessions/year)",
            "Physical therapy (up to 30 sessions/year)",
            "Laboratory tests (comprehensive panel)",
            "Ambulance services (ground)",
            "Post-surgical rehabilitation (up to 15 sessions)",
            "Home health visits (up to 10/year)",
            "Diabetes management program",
            "Cardiac monitoring and stress tests",
        ]),
        "exclusions": json.dumps([
            "Cosmetic surgery (aesthetic only)",
            "Fertility treatments and IVF",
            "Experimental treatments",
            "Dental implants and orthodontics",
            "Vision correction surgery (LASIK)",
            "Air ambulance",
            "Long-term custodial nursing home care",
            "Non-DCGI approved medications",
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
                "keywords": json.dumps(["eligibility", "age", "qualify", "enrollment", "standard plan requirements"]),
                "section_content": """Standard Health Plan — Eligibility Requirements

WHO CAN ENROLL:
- Age: 18 to 70 years at the time of enrollment (wider range than Basic plan)
- Must be a resident of India with valid Aadhaar or PAN
- Individual or family coverage available
- No active insurance fraud history

PRE-EXISTING CONDITIONS:
Reduced 6-month waiting period (vs. 12 months for Basic plan). All common conditions accepted including diabetes, hypertension, heart disease, asthma, COPD, thyroid disorders, mental health conditions, and cancer history.

SURCHARGES:
- Smokers: 20% surcharge on base premium (lower than Basic plan's 25%)
- BMI 30 or above: 10% surcharge (lower than Basic plan's 15%)
- Both surcharges may apply simultaneously

FAMILY ENROLLMENT:
- Spouse: Same premium as individual; must enroll separately
- Children (0 to 25 if full-time student, otherwise 0 to 18): Rs 800/month add-on per child

ENROLLMENT WINDOWS:
- Annual open enrollment (October 1 to November 30)
- Qualifying life events: within 30 days of marriage, birth, adoption, job loss
- New employees: within 60 days of employment start""",
            },
            {
                "section_title": "Covered Services and Benefits",
                "section_number": 2,
                "keywords": json.dumps(["coverage", "covered", "services", "benefits", "standard plan", "what is covered", "hospitalization", "specialist", "MRI"]),
                "section_content": """Standard Health Plan — Covered Services and Benefits

EMERGENCY AND HOSPITAL:
- Emergency room: full coverage after deductible and 20% copay
- Hospital stays: semi-private room (2-bed ward)
- ICU/CCU: covered for medically necessary stays (no cap on duration)
- Pre-operative and post-operative care
- Surgical fees, anesthesiology, pathology during hospitalization
- In-hospital medications (all DCGI-approved drugs)

PHYSICIAN VISITS:
- Unlimited primary care physician visits
- Up to 20 specialist consultations per year (no referral required for 10 of these)
- Telemedicine consultations: unlimited (via HealthInsure app)
- Second opinion: 1 covered second opinion per year for major diagnoses

PRESCRIPTION MEDICATIONS:
- Generic medications: fully covered after copay
- Brand-name medications: covered after copay (formulary restrictions apply)
- Specialty medications: requires prior authorization
- 90-day mail-order supply available for maintenance medications

MENTAL HEALTH SERVICES:
- Up to 24 outpatient therapy sessions per year
- Psychiatrist consultations: up to 6 per year
- Crisis intervention and emergency psychiatric care: covered
- Inpatient psychiatric stays: up to 30 days per year
- Substance abuse treatment: 15 outpatient sessions per year
- Covered conditions: depression, anxiety, PTSD, bipolar disorder, OCD, schizophrenia

PHYSICAL THERAPY AND REHABILITATION:
- Up to 30 sessions per year for injury, post-surgical recovery, or chronic condition management
- Occupational therapy: up to 10 sessions
- Speech therapy: up to 10 sessions (for stroke recovery, etc.)

DIAGNOSTIC IMAGING:
- X-rays: unlimited; Ultrasound: unlimited; MRI scans: up to 4 per year
- CT scans: up to 4 per year; PET scans: 1 per year (for cancer staging)
- Echocardiogram and cardiac stress test: 1 per year each

MATERNITY (AFTER 6-MONTH WAITING PERIOD):
- Prenatal visits: up to 12 per pregnancy
- Delivery (normal and cesarean): covered
- Postnatal care: up to 6 weeks
- Newborn care: first 30 days covered under mother's policy""",
            },
            {
                "section_title": "Exclusions and Limitations",
                "section_number": 3,
                "keywords": json.dumps(["exclusion", "not covered", "limitation", "excluded", "denied", "standard plan exclusions"]),
                "section_content": """Standard Health Plan — Exclusions and Limitations

COMPLETELY EXCLUDED:
- Cosmetic procedures: rhinoplasty, facelifts, liposuction, breast augmentation, tattooing
- Fertility treatments: IVF, IUI, ICSI, egg freezing, gamete banking
- Experimental treatments: non-DCGI-approved therapies, unregistered clinical trials
- Dental implants and orthodontics (basic dental emergencies are covered)
- LASIK and other elective vision correction surgeries
- Air ambulance transport
- Long-term custodial nursing home care unrelated to acute medical treatment
- Non-DCGI-approved medications and supplements

ANNUAL LIMITS:
- Total coverage: Rs 15,00,000 per year
- Specialist visits: 20 per year; Physical therapy: 30 sessions per year
- Mental health outpatient: 24 sessions per year
- Inpatient psychiatric: 30 days per year
- MRI and CT scans: 4 each per year
- Home health visits: 10 per year

COST SHARING:
- Annual deductible: Rs 15,000
- Copay: 20% of covered services after deductible
- Out-of-pocket maximum: Rs 1,50,000 per year. After this, plan covers 100%.
- Example: Rs 2,00,000 surgery means you pay Rs 15,000 deductible + Rs 37,000 copay = Rs 52,000 out-of-pocket

WAITING PERIODS:
- Pre-existing conditions: 6-month waiting period
- Maternity: 6-month waiting period
- All other services: covered from Day 1""",
            },
            {
                "section_title": "Mental Health and Substance Abuse Coverage",
                "section_number": 4,
                "keywords": json.dumps(["mental health", "therapy", "psychiatry", "depression", "anxiety", "counseling", "substance abuse", "addiction"]),
                "section_content": """Standard Health Plan — Mental Health and Substance Abuse Coverage

OUTPATIENT MENTAL HEALTH:
- 24 therapy/counseling sessions per year (individual, group, or family therapy)
- Licensed psychologist, clinical social worker, or licensed counselor
- Psychiatric consultation: 6 visits per year
- Telemedicine mental health consultations: counted toward the 24-session limit

INPATIENT PSYCHIATRIC CARE:
- Up to 30 days per year at an accredited psychiatric facility
- Includes acute psychiatric crisis stabilization
- Partial hospitalization programs (PHP): up to 40 days per year

COVERED MENTAL HEALTH CONDITIONS:
- Major depressive disorder, generalized anxiety disorder, panic disorder
- Bipolar disorder (Types I and II)
- Post-traumatic stress disorder (PTSD)
- Obsessive-compulsive disorder (OCD)
- Schizophrenia and schizoaffective disorder
- Eating disorders (anorexia, bulimia): inpatient only

SUBSTANCE ABUSE TREATMENT:
- 15 outpatient sessions per year
- Inpatient detox: up to 7 days per year (medically supervised)
- Medication-assisted treatment (e.g., buprenorphine, naltrexone): covered under prescription benefit

HOW TO ACCESS MENTAL HEALTH SERVICES:
- No referral required for mental health providers in our network
- Find providers: healthinsure.in/mental-health-providers
- Crisis line (24/7): 1800-XXX-MIND (6463)""",
            },
            {
                "section_title": "Pre-authorization Requirements",
                "section_number": 5,
                "keywords": json.dumps(["pre-authorization", "prior authorization", "approval", "preapproval", "need approval", "authorization required"]),
                "section_content": """Standard Health Plan — Pre-authorization Requirements

SERVICES REQUIRING PRE-AUTHORIZATION:
- All planned hospitalizations (non-emergency): required 48 hours in advance
- Specialist consultations beyond the 10 self-referral limit
- MRI and CT scans
- Inpatient psychiatric stays
- Physical therapy beyond 10 sessions
- Home health services
- Specialty medications
- Surgical procedures (non-emergency)
- Chemotherapy and radiation therapy

SERVICES NOT REQUIRING PRE-AUTHORIZATION:
- Emergency room visits
- Primary care physician visits
- Routine preventive care
- Lab tests ordered by your physician
- Generic and standard brand-name prescriptions
- Telehealth consultations (first 10 per year)

HOW TO GET PRE-AUTHORIZATION:
1. Your doctor submits a pre-authorization request on your behalf (preferred)
2. Or call 1800-XXX-1111 with: patient name, policy number, diagnosis code, procedure code, treating physician name, planned date
3. Online: submit at healthinsure.in/pre-auth
4. Decision within: 3 business days standard; 1 business day urgent

IF PRE-AUTHORIZATION IS DENIED:
- Request a peer-to-peer review (your doctor speaks directly to our medical reviewer)
- File an appeal within 60 days
- Expedited appeals for urgent medical situations: decision within 72 hours""",
            },
            {
                "section_title": "Prescription Drug Coverage",
                "section_number": 6,
                "keywords": json.dumps(["medication", "prescription", "drugs", "pharmacy", "brand name", "generic", "formulary", "mail order"]),
                "section_content": """Standard Health Plan — Prescription Drug Coverage

DRUG TIERS AND COST SHARING (after deductible):
- Tier 1 (Generic): 20% copay; maximum Rs 200 per prescription
- Tier 2 (Preferred Brand-Name): 20% copay; maximum Rs 500 per prescription
- Tier 3 (Non-Preferred Brand): 20% copay; maximum Rs 1,000 per prescription
- Tier 4 (Specialty Drugs): 20% copay with prior authorization; maximum Rs 2,000 per fill

MAIL-ORDER PHARMACY:
- 90-day supply for maintenance medications (chronic condition drugs)
- 10% discount vs. retail pharmacy; free delivery to registered address
- Enroll at healthinsure.in/mail-order

COVERED MEDICATION CATEGORIES:
- Diabetes medications (all approved types including GLP-1 agonists with prior auth)
- Cardiovascular medications (statins, ACE inhibitors, beta-blockers, blood thinners)
- Respiratory medications (all inhalers, oral steroids, leukotriene modifiers)
- Mental health medications (antidepressants, antipsychotics, mood stabilizers, anxiolytics)
- Thyroid medications, blood pressure medications
- Antibiotics, antivirals, pain management (NSAIDs, limited opioids with prior auth)
- Cancer medications (with prior authorization)

SPECIALTY DRUGS (Require Prior Authorization):
- Biologics for autoimmune conditions (rheumatoid arthritis, psoriasis, Crohn's)
- Insulin analogs and continuous glucose monitors
- Multiple sclerosis medications, HIV antiretroviral therapy""",
            },
            {
                "section_title": "Claims Filing and Reimbursement Process",
                "section_number": 7,
                "keywords": json.dumps(["claim", "submit", "reimbursement", "file", "how to claim", "documents", "appeal", "denied claim"]),
                "section_content": """Standard Health Plan — Claims Filing and Reimbursement Process

CASHLESS CLAIMS (at network hospitals):
1. Get pre-authorization if required (planned admissions)
2. Show HealthInsure card at hospital admission desk
3. Hospital submits claim directly to HealthInsure
4. You pay only your deductible and 20% copay at discharge
5. Track status: healthinsure.in/claims or HealthInsure app

REIMBURSEMENT CLAIMS (out-of-network or paid upfront):
1. Pay the full bill upfront
2. Log in to portal within 90 days of service
3. Upload: itemized bill, discharge summary, prescriptions, lab reports, proof of payment
4. Processing: 15 to 20 business days
5. Payment via NEFT to registered account within 7 days of approval

PROCESSING TIMES:
- Cashless: Pre-approval 3 days; final settlement 7 days post-discharge
- Reimbursement: 15 to 20 business days
- Emergency reimbursement: 5 to 10 business days (mark as URGENT)

APPEAL PROCESS:
- File within 60 days of denial
- Required: denial letter, additional medical records, physician statement
- Decision within 30 days; second-level appeal available
- External review available for complex denials
- Contact: appeals@healthinsure.in or 1800-XXX-2222""",
            },
            {
                "section_title": "Frequently Asked Questions — Standard Plan",
                "section_number": 8,
                "keywords": json.dumps(["FAQ", "questions", "standard plan FAQ", "common questions", "help", "how much", "what is covered"]),
                "section_content": """Standard Health Plan — Frequently Asked Questions

Q: What is the out-of-pocket maximum on the Standard plan?
A: Rs 1,50,000 per year. After you have paid Rs 1,50,000 in deductibles and copays combined, the plan covers 100% of remaining covered expenses for the rest of the year.

Q: Can I see a specialist without a referral?
A: Yes, for the first 10 specialist visits per year, no referral is needed. After 10 visits, a referral from your primary care physician is required.

Q: Does the Standard plan cover maternity?
A: Yes, after a 6-month waiting period. Prenatal visits (up to 12), delivery (normal and cesarean), and postnatal care are covered.

Q: How many therapy sessions do I get for mental health?
A: 24 outpatient sessions per year. Inpatient psychiatric stays are covered up to 30 days per year.

Q: Is there a limit on primary care visits?
A: No. Unlimited primary care visits are covered under the Standard plan.

Q: Are MRI and CT scans covered?
A: Yes. Up to 4 MRI scans and 4 CT scans per year. Pre-authorization is required.

Q: Does the Standard plan cover dental?
A: Emergency dental care (e.g., tooth extraction due to injury or infection) is covered. Routine dental, implants, and orthodontics are not.

Q: What is the waiting period for pre-existing conditions?
A: 6 months. After 6 months, all pre-existing conditions are fully covered as per plan benefits.

Q: Does the plan cover diabetes medications?
A: Yes. Metformin and other oral diabetes medications are covered at Tier 1. GLP-1 agonists require prior authorization at Tier 4.

Q: I have hypertension. When can I claim for my blood pressure medications?
A: After the 6-month waiting period, your hypertension medications and doctor visits are fully covered.

Q: Can I use telemedicine?
A: Yes. Unlimited telemedicine consultations through the HealthInsure app for primary care and mental health.""",
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
            "Emergency room visits (full, including air ambulance)",
            "Hospital stays (private room, full ICU/CCU)",
            "Primary care physician visits (unlimited)",
            "Specialist consultations (unlimited, no referral)",
            "Generic, brand-name, and specialty prescription medications",
            "Preventive care and executive health screenings",
            "All diagnostic imaging (unlimited MRI, CT, PET)",
            "Mental health services (unlimited outpatient and inpatient)",
            "Physical therapy (unlimited sessions)",
            "Dental care (preventive, basic, major — up to Rs 50,000/year)",
            "Vision care (exams, glasses, contacts — up to Rs 10,000/year)",
            "Maternity and newborn care (full prenatal to postnatal)",
            "Rehabilitation services (all types)",
            "Home health care services",
            "International emergency coverage (up to Rs 5,00,000/trip)",
            "Organ transplant (recipient and related donor costs)",
            "Cancer care program (full oncology team support)",
            "Personal health concierge service",
        ]),
        "exclusions": json.dumps([
            "Non-reconstructive cosmetic surgery",
            "Experimental treatments not in approved clinical trials",
            "Elective weight loss surgery (unless BMI 40+ with comorbidities)",
            "IVF (available as optional rider)",
            "Surrogacy-related medical costs",
        ]),
        "age_min": 0,
        "age_max": 75,
        "smoker_surcharge_pct": 15.0,
        "bmi_surcharge_pct": 8.0,
        "pre_existing_waiting_months": 3,
        "sections": [
            {
                "section_title": "Eligibility and Enrollment",
                "section_number": 1,
                "keywords": json.dumps(["eligibility", "age", "qualify", "enrollment", "who can join", "premium plan"]),
                "section_content": """Premium Health Plan — Eligibility and Enrollment

WHO CAN ENROLL:
- Age: 0 to 75 years (covers newborns, children, adults, and seniors)
- Indian residents with valid Aadhaar or PAN
- Individuals, families, or corporate groups
- Non-resident Indians (NRIs) with valid Indian address: eligible for India-based care

PRE-EXISTING CONDITIONS:
Only 3-month waiting period — the shortest available. All conditions accepted including history of cancer, organ transplants, and chronic diseases.

SURCHARGES (LOWEST AVAILABLE):
- Smokers: 15% surcharge (vs 20 to 25% on other plans)
- BMI 30+: 8% surcharge (vs 10 to 15% on other plans)

FAMILY COVERAGE:
- Spouse: Rs 4,500/month; Children 0 to 18: Rs 2,000/month per child
- Adult dependents (parents, in-laws) 18 to 75: Rs 4,000/month
- Family floater option: Rs 18,000/month for up to 2 adults + 3 children

ENROLLMENT:
- Anytime enrollment (no restricted open enrollment period for Premium)
- Coverage begins within 24 hours of enrollment confirmation""",
            },
            {
                "section_title": "Comprehensive Covered Services",
                "section_number": 2,
                "keywords": json.dumps(["coverage", "covered", "services", "benefits", "premium plan", "everything covered", "comprehensive"]),
                "section_content": """Premium Health Plan — Comprehensive Covered Services

EMERGENCY AND HOSPITAL (No network restrictions):
- Emergency room: full coverage including trauma centers
- Air ambulance: covered up to Rs 2,00,000 per incident
- Private room hospitalization (unlimited duration)
- Full ICU/CCU coverage, all surgical procedures
- Transplant surgery: recipient + related living donor costs

PHYSICIAN ACCESS:
- Unlimited primary care and specialist visits
- No referrals required for any specialist
- Concierge physician service (home/office visits by appointment)
- International second opinion: 1 per year covered up to Rs 50,000

DENTAL (Annual limit: Rs 50,000):
- Preventive: cleanings, X-rays, fluoride (2x per year, no copay)
- Basic restorative: fillings, extractions, root canals
- Major restorative: crowns, bridges, partial dentures
- Children's orthodontics: coverage up to Rs 15,000 lifetime maximum

VISION (Annual limit: Rs 10,000):
- Annual comprehensive eye exam (Rs 0 copay)
- Prescription eyeglasses: up to Rs 3,000 per year
- Contact lenses: up to Rs 5,000 per year

MATERNITY AND NEWBORN:
- Full prenatal care (unlimited visits, all recommended tests)
- Delivery: normal, C-section, VBAC
- Postnatal care: 12 weeks for mother
- Newborn: covered under mother's policy from birth to 90 days

CANCER CARE PROGRAM:
- Dedicated oncology care coordinator
- Chemotherapy, radiation therapy, targeted therapy, immunotherapy
- Oncology surgery, pain management, palliative and hospice care (up to 6 months)

MENTAL HEALTH (Fully parity with medical benefits):
- Unlimited outpatient therapy sessions
- Unlimited psychiatric consultations and inpatient psychiatric stays
- Substance abuse (inpatient detox + outpatient therapy): unlimited""",
            },
            {
                "section_title": "Dental and Vision Coverage Details",
                "section_number": 3,
                "keywords": json.dumps(["dental", "vision", "teeth", "eye", "glasses", "contact lenses", "root canal", "crown", "filling", "eye exam"]),
                "section_content": """Premium Health Plan — Dental and Vision Coverage Details

DENTAL COVERAGE (Annual Maximum: Rs 50,000):

PREVENTIVE DENTAL (No copay, no deductible):
- Oral examinations: 2 per year
- Professional teeth cleaning: 2 per year
- Dental X-rays: bitewing X-rays annually; panoramic every 3 years
- Fluoride treatment: adults 1/year; children 2/year
- Dental sealants: covered for children up to age 14

BASIC RESTORATIVE (10% copay after Rs 500 dental deductible):
- Fillings (composite/tooth-colored): all teeth
- Simple and surgical tooth extractions
- Emergency palliative treatment
- Periodontal scaling and root planing (deep cleaning): 1 per year

MAJOR RESTORATIVE (10% copay):
- Root canals (all teeth), crowns (porcelain, metal)
- Fixed dental bridges, partial and complete dentures
- Bone grafting (when required for medically necessary procedure)

ORTHODONTICS (Children only, up to age 18):
- Coverage up to Rs 15,000 lifetime maximum
- Traditional braces and clear aligners, retainers

VISION COVERAGE (Annual Maximum: Rs 10,000):
- Comprehensive eye examination: 1 per year (Rs 0 copay)
- Eyeglass frames: up to Rs 3,000 per year
- Eyeglass lenses (single vision, bifocal, progressive): up to Rs 4,000 per year
- Contact lenses (in lieu of glasses): up to Rs 5,000 per year
- LASIK for medical necessity (keratoconus): covered with prior authorization
- Elective LASIK for vision correction: NOT covered""",
            },
            {
                "section_title": "Maternity and Newborn Coverage",
                "section_number": 4,
                "keywords": json.dumps(["maternity", "pregnancy", "delivery", "newborn", "prenatal", "postnatal", "baby", "childbirth", "IUI"]),
                "section_content": """Premium Health Plan — Maternity and Newborn Coverage

WAITING PERIOD FOR MATERNITY: 3 months (same as all other conditions)

PRENATAL CARE:
- Unlimited OB/GYN visits throughout pregnancy
- All recommended prenatal blood tests
- Ultrasounds: dating scan, anomaly scan, growth scans — all covered
- Non-invasive prenatal testing (NIPT): covered
- High-risk pregnancy management: covered including maternal-fetal medicine specialist
- Nutrition counseling and prenatal classes: up to 10 sessions covered

DELIVERY:
- Normal vaginal delivery, Cesarean section (planned or emergency), VBAC
- Labor and delivery room, epidural analgesia
- Neonatologist attendance at delivery

POSTNATAL CARE:
- Mother: 12 weeks of postnatal care visits
- Postnatal depression screening and treatment
- Lactation consultant: up to 6 visits
- Postpartum physical therapy: up to 6 sessions

NEWBORN CARE:
- Covered under mother's policy from birth to 90 days
- NICU stays: covered (no separate enrollment required)
- Newborn screening tests, immunizations from birth schedule
- Must be enrolled as separate member after 90 days

FERTILITY COVERAGE (LIMITED):
- IUI (Intrauterine Insemination): 3 cycles per year
- Fertility consultations and hormonal testing: covered
- Ovulation induction medications: covered under prescription benefit
- IVF, ICSI, egg freezing: NOT covered in base plan (available as optional Premium Plus Fertility Rider)

COMPLICATIONS OF PREGNANCY:
- All pregnancy complications covered: preeclampsia, gestational diabetes, ectopic pregnancy, miscarriage management""",
            },
            {
                "section_title": "Pre-existing Conditions and Chronic Disease Management",
                "section_number": 5,
                "keywords": json.dumps(["pre-existing", "chronic disease", "diabetes management", "heart disease", "cancer", "kidney", "waiting period"]),
                "section_content": """Premium Health Plan — Pre-existing Conditions and Chronic Disease Management

3-MONTH WAITING PERIOD APPLIES TO ALL PRE-EXISTING CONDITIONS.

CHRONIC DISEASE MANAGEMENT PROGRAM (Included at no extra cost):

DIABETES MANAGEMENT:
- Dedicated diabetes care coordinator
- HbA1c testing every 3 months (covered)
- Continuous glucose monitor (CGM): covered up to Rs 24,000/year
- Diabetic educator: 4 sessions per year
- Annual diabetic foot exam and annual ophthalmology exam for diabetic retinopathy
- All diabetes medications covered (including latest GLP-1 agonists with prior auth)
- Insulin and insulin supplies: fully covered

CARDIOVASCULAR DISEASE:
- Cardiologist: unlimited consultations
- Annual echocardiogram and stress test
- All cardiac medications covered
- Cardiac rehabilitation: up to 36 sessions after heart attack or surgery

HYPERTENSION:
- All blood pressure medications covered
- 24-hour ambulatory blood pressure monitoring: 1 per year

CANCER:
- Full oncology team: medical oncologist, surgical oncologist, radiation oncologist
- All DCGI-approved chemotherapy, targeted therapy, immunotherapy
- Radiation therapy, bone marrow transplant (autologous and allogeneic): covered
- Cancer genetic counseling and BRCA testing
- Palliative and hospice care

KIDNEY DISEASE:
- Nephrologist: unlimited visits; dialysis: fully covered
- Kidney transplant preparation, surgery, and post-transplant immunosuppressants""",
            },
            {
                "section_title": "Cost Sharing and Out-of-Pocket Maximum",
                "section_number": 6,
                "keywords": json.dumps(["cost", "deductible", "copay", "out of pocket", "maximum", "how much to pay", "cost sharing", "premium cost"]),
                "section_content": """Premium Health Plan — Cost Sharing and Out-of-Pocket Maximum

ANNUAL DEDUCTIBLE: Rs 5,000 (lowest available across all plans)
- Must be paid before insurance pays for most services
- Preventive care, dental preventive, and wellness visits do NOT require deductible

COPAY AFTER DEDUCTIBLE: 10% (lowest available)
- You pay only 10% of covered service costs; plan pays 90%
- Example: Rs 1,00,000 surgery means you pay Rs 5,000 deductible + Rs 9,500 copay = Rs 14,500 out-of-pocket

OUT-OF-POCKET MAXIMUM:
- Individual: Rs 50,000 per year
- Family: Rs 1,00,000 per year
- Once you reach the out-of-pocket maximum, the plan pays 100% of all covered services for the rest of the year

PREMIUM PRICING EXAMPLES (Monthly):
- Age 28, non-smoker, BMI 22: Rs 5,500/month (base rate)
- Age 35, non-smoker, BMI 26.2: Rs 6,050/month (age +10%)
- Age 35, smoker, BMI 22: Rs 6,957/month (age + smoker surcharge)
- Age 50, non-smoker, BMI 31: Rs 7,128/month (age + BMI surcharge)
- Age 50, smoker, BMI 31: Rs 8,205/month (all surcharges)

PRESCRIPTION DRUG COST SHARING:
- All tiers: 10% copay after medical deductible
- Specialty drugs with prior auth: 10% copay, max Rs 1,500 per fill

DENTAL COST SHARING:
- Preventive dental: Rs 0 copay (no deductible applied)
- Restorative dental: 10% copay after Rs 500 dental deductible (separate from medical deductible)""",
            },
            {
                "section_title": "Claims Process and Appeals",
                "section_number": 7,
                "keywords": json.dumps(["claim", "submit", "appeal", "denied", "reimbursement", "premium claim", "fast track", "process"]),
                "section_content": """Premium Health Plan — Claims Process and Appeals

CASHLESS TREATMENT (Preferred):
- Available at all 5,000+ network hospitals in India
- Show HealthInsure Premium card; hospital bills insurer directly
- You pay only Rs 5,000 deductible + 10% copay at discharge

FAST-TRACK CLAIM PROCESSING:
- Premium members: claims processed within 5 to 10 business days
- Emergency claims: 24 to 48 hour initial response; full settlement within 5 business days
- Dedicated claims team: premiumclaims@healthinsure.in

CLAIM SUBMISSION FOR REIMBURSEMENT:
1. Upload documents at healthinsure.in/claims or via app
2. Required: itemized bills, discharge summary, doctor notes, test reports, proof of payment
3. 180-day submission window (vs. 90 days for other plans)

APPEALS:
- Standard appeal: file within 90 days (vs. 60 for other plans)
- Urgent/expedited appeal (medical necessity): 72-hour decision
- Peer-to-peer review available
- External independent review available if internal appeal denied
- Success rate: 40% of appeals result in coverage approval

24/7 CLAIMS SUPPORT:
- Phone: 1800-XXX-PREM (7736)
- Chat: HealthInsure app
- Email: premiumclaims@healthinsure.in
- Dedicated case manager assigned for claims over Rs 5,00,000""",
            },
            {
                "section_title": "International Coverage and Additional Benefits",
                "section_number": 8,
                "keywords": json.dumps(["international", "travel", "abroad", "foreign", "overseas", "concierge", "wellness", "gym", "additional benefits"]),
                "section_content": """Premium Health Plan — International Coverage and Additional Benefits

INTERNATIONAL EMERGENCY COVERAGE:
- Covered up to Rs 5,00,000 per trip for emergency medical care outside India
- Applies to trips up to 90 consecutive days outside India
- Medical evacuation to India: covered up to Rs 3,00,000
- International second opinion: 1 per year from specialists in USA, UK, Singapore — up to Rs 50,000

HOW TO USE INTERNATIONAL COVERAGE:
1. Carry your HealthInsure Premium card and travel certificate
2. In an emergency, go to the nearest hospital
3. Pay upfront (most international hospitals require this)
4. Submit reimbursement claim within 90 days of returning to India
5. Include: bills, hospital records, passport copy, travel dates

PERSONAL HEALTH CONCIERGE SERVICE:
Every Premium member gets a dedicated health concierge who helps:
- Coordinate specialist appointments (same-week appointments at partner hospitals)
- Arrange second opinions (domestic and international)
- Navigate complex diagnoses and treatment plans
- Manage hospital admissions and discharge planning
- 24/7 availability: chat, phone, and email

WELLNESS PROGRAMS (Covered):
- Annual executive health check-up at partner diagnostic centers (value: Rs 15,000)
- Personalized health coaching: 6 sessions per year
- Nutrition counseling: 6 sessions per year
- Smoking cessation program: medications + counseling covered for 6 months
- Mindfulness and meditation app subscription

PREVENTIVE HEALTH SCREENINGS (Comprehensive annual package):
- Full blood panel (40+ markers), cardiac risk assessment
- Diabetic screening (fasting glucose, HbA1c), cancer markers
- Thyroid function, liver and kidney function, chest X-ray
- Bone density scan (age 50+), colonoscopy (age 45+)""",
            },
            {
                "section_title": "Exclusions and Limitations",
                "section_number": 9,
                "keywords": json.dumps(["exclusion", "not covered", "limitation", "excluded", "premium plan exclusions"]),
                "section_content": """Premium Health Plan — Exclusions and Limitations

The Premium plan has the fewest exclusions of any HealthInsure plan.

EXCLUDED SERVICES:
1. Non-Reconstructive Cosmetic Surgery:
   - Rhinoplasty, facelifts, liposuction, breast augmentation/reduction (for cosmetic reasons)
   - INCLUDED: Reconstructive procedures following accidents, burns, mastectomy, or birth defects

2. Experimental Treatments (not in approved clinical trials):
   - Stem cell therapy (except bone marrow transplants for blood cancers)
   - Gene therapy not approved by DCGI
   - Alternative therapies: Ayurveda, homeopathy, naturopathy, Reiki

3. Elective Weight Loss Surgery:
   - Bariatric surgery NOT covered unless: BMI 40 or higher, or BMI 35+ with serious comorbidities (diabetes, hypertension, sleep apnea, cardiovascular disease)
   - Two independent physicians must recommend the surgery

4. IVF and Advanced Fertility:
   - IVF, ICSI, egg freezing, embryo storage: not covered under base plan
   - Available as an optional rider: contact sales@healthinsure.in

5. Surrogacy:
   - Surrogate mother's medical costs: not covered
   - Intended parent's newborn care IS covered from birth

IMPORTANT NOTES:
- If a service is not listed as excluded, it is covered
- For any doubt about coverage, call 1800-XXX-CARE (2273) before the service
- Medically necessary vs. elective determinations made by our medical review team within 3 business days""",
            },
            {
                "section_title": "Frequently Asked Questions — Premium Plan",
                "section_number": 10,
                "keywords": json.dumps(["FAQ", "premium plan questions", "what is covered", "help", "common questions"]),
                "section_content": """Premium Health Plan — Frequently Asked Questions

Q: What is the out-of-pocket maximum?
A: Rs 50,000 per individual per year. After this, the plan covers 100% of all eligible expenses.

Q: I have diabetes. When can I start claiming for diabetes-related treatment?
A: After the 3-month waiting period. Diabetes medications, HbA1c tests, endocrinologist visits, and continuous glucose monitors are fully covered from month 4.

Q: Does the Premium plan cover dental implants?
A: Base implant costs are not covered. Bone grafting related to medically necessary extractions is covered. Implants may be covered if tooth loss was due to an accident — contact your health concierge to verify.

Q: Can I see any specialist without a referral?
A: Yes. The Premium plan covers unlimited specialist visits with no referral required.

Q: Is international travel covered?
A: Emergency medical care abroad is covered up to Rs 5,00,000 per trip (trips up to 90 days). Routine or planned care abroad is not covered.

Q: Does the plan cover LASIK eye surgery?
A: Elective LASIK for vision correction is not covered. LASIK for medical necessity (e.g., keratoconus) is covered with prior authorization.

Q: Is IVF covered?
A: IVF is not included in the base Premium plan. IUI (3 cycles/year) is covered. An optional Premium Plus Fertility Rider is available for IVF coverage.

Q: My elderly parent is 72 years old. Can they enroll?
A: Yes. The Premium plan covers individuals up to age 75 at enrollment.

Q: What is the concierge service?
A: Every Premium member gets a dedicated health concierge — a personal healthcare assistant who helps coordinate care, book specialist appointments, and manage complex diagnoses 24/7.

Q: How quickly are claims processed?
A: Premium claims are fast-tracked: 5 to 10 business days for standard claims; 24 to 48 hours for emergency claims.

Q: Does the plan cover mental health?
A: Yes, completely. Unlimited outpatient therapy, unlimited psychiatric care, and unlimited inpatient psychiatric stays are covered.

Q: My BMI is 32. What surcharge do I pay?
A: An 8% surcharge on the base monthly premium of Rs 5,500. Your monthly premium would be Rs 5,500 x 1.08 = Rs 5,940 (before any age adjustments).

Q: I have hypertension and diabetes. Will both conditions be covered?
A: Yes, both conditions are covered after the 3-month waiting period. You will have access to the chronic disease management program for both conditions.""",
            },
        ],
    },
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        existing_policies = db.query(Policy).count()

        if existing_policies == 0:
            # Fresh seed
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
        else:
            # Update existing policies — add missing sections and update fields
            for policy_data in POLICIES:
                sections_data = policy_data.pop("sections")
                policy = db.query(Policy).filter(Policy.name == policy_data["name"]).first()
                if not policy:
                    policy = Policy(**policy_data)
                    db.add(policy)
                    db.commit()
                    db.refresh(policy)
                    print(f"Created new policy: {policy.name}")
                else:
                    # Update policy fields
                    for key, value in policy_data.items():
                        setattr(policy, key, value)
                    db.commit()

                existing_section_numbers = {
                    s.section_number for s in
                    db.query(PolicySection).filter(PolicySection.policy_id == policy.id).all()
                }

                added = 0
                for section_data in sections_data:
                    if section_data["section_number"] not in existing_section_numbers:
                        section = PolicySection(policy_id=policy.id, **section_data)
                        db.add(section)
                        added += 1
                    else:
                        # Update existing section content
                        existing = db.query(PolicySection).filter(
                            PolicySection.policy_id == policy.id,
                            PolicySection.section_number == section_data["section_number"]
                        ).first()
                        if existing:
                            existing.section_content = section_data["section_content"]
                            existing.section_title = section_data["section_title"]
                            existing.keywords = section_data["keywords"]

                db.commit()
                if added > 0:
                    print(f"Added {added} new sections to {policy.name}")
                else:
                    print(f"{policy.name}: updated existing sections")

        print("Building FAISS vector store...")
        build_vector_store(db)
        print("Seed/update complete!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
