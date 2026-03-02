import json
import re


KNOWN_CONDITIONS = [
    "diabetes", "heart disease", "hypertension", "cancer", "asthma",
    "copd", "kidney disease", "liver disease", "stroke", "arthritis",
    "depression", "anxiety", "obesity", "thyroid", "epilepsy",
    "dental", "vision", "maternity", "pregnancy", "fertility",
    "cosmetic", "mental health", "physical therapy", "rehabilitation",
]

INTENT_KEYWORDS = {
    "eligibility": ["eligible", "eligibility", "qualify", "qualification", "can i", "am i", "do i qualify"],
    "coverage": ["cover", "coverage", "covered", "include", "included", "what does", "does it cover", "is it covered"],
    "exclusion": ["exclude", "exclusion", "not covered", "excluded", "what is not", "what isn't", "not include"],
    "premium": ["premium", "cost", "price", "how much", "monthly", "payment", "afford", "rate", "fee"],
    "deductible": ["deductible", "out of pocket", "copay", "co-pay", "cost sharing"],
    "claims": ["claim", "file", "submit", "reimbursement", "reimburse", "pending", "my claims", "claim status"],
    "waiting_period": ["waiting period", "pre-existing", "waiting", "how long", "when can i"],
    "comparison": ["compare", "comparison", "difference", "better", "vs", "versus", "which plan", "best plan"],
    "profile": ["my profile", "my conditions", "my age", "my bmi", "my health", "about me", "my details"],
}


def _calculate_personalized_premium(policy, age, bmi, is_smoker) -> tuple[float, list[str]]:
    """Calculate actual monthly premium for this specific patient."""
    premium = policy.monthly_premium_base
    notes = []

    if age:
        if age > 55:
            premium *= 1.30
            notes.append(f"age {age} group (+30%)")
        elif age > 45:
            premium *= 1.20
            notes.append(f"age {age} group (+20%)")
        elif age > 35:
            premium *= 1.10
            notes.append(f"age {age} group (+10%)")

    if is_smoker and policy.smoker_surcharge_pct > 0:
        premium *= (1 + policy.smoker_surcharge_pct / 100)
        notes.append(f"smoker surcharge (+{policy.smoker_surcharge_pct:.0f}%)")

    if bmi and bmi > 30 and policy.bmi_surcharge_pct > 0:
        premium *= (1 + policy.bmi_surcharge_pct / 100)
        notes.append(f"BMI {bmi:.1f} surcharge (+{policy.bmi_surcharge_pct:.0f}%)")

    return premium, notes


class EligibilityAssessor:

    def classify_intent(self, query: str) -> list[str]:
        query_lower = query.lower()
        intents = []
        for intent, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    intents.append(intent)
                    break
        if not intents:
            intents = ["general"]
        return intents

    def extract_condition_mentions(self, query: str) -> list[str]:
        query_lower = query.lower()
        found = []
        for condition in KNOWN_CONDITIONS:
            if condition in query_lower:
                found.append(condition)
        return found

    def check_age_eligibility(self, age: int, policy) -> dict:
        if age is None:
            return {"eligible": None, "message": "Age not provided. Cannot check age eligibility."}
        if policy.age_min <= age <= policy.age_max:
            return {
                "eligible": True,
                "message": f"You meet the age requirement ({policy.age_min}-{policy.age_max} years) for {policy.name}.",
            }
        else:
            return {
                "eligible": False,
                "message": f"You do not meet the age requirement ({policy.age_min}-{policy.age_max} years) for {policy.name}. Your age: {age}.",
            }

    def check_coverage(self, query: str, retrieved_sections: list, conditions: list, policy) -> dict:
        coverage_list = []
        try:
            coverage_list = json.loads(policy.coverage_details or "[]")
        except (json.JSONDecodeError, TypeError):
            pass

        exclusion_list = []
        try:
            exclusion_list = json.loads(policy.exclusions or "[]")
        except (json.JSONDecodeError, TypeError):
            pass

        covered_items = []
        excluded_items = []

        for cond in conditions:
            cond_lower = cond.lower()
            is_excluded = any(cond_lower in exc.lower() for exc in exclusion_list)
            is_covered = any(cond_lower in cov.lower() for cov in coverage_list)

            if is_excluded:
                excluded_items.append(cond)
            elif is_covered:
                covered_items.append(cond)

        section_coverage_info = []
        for section in retrieved_sections:
            content = section.page_content.lower() if hasattr(section, "page_content") else ""
            for cond in conditions:
                if cond.lower() in content:
                    section_coverage_info.append({
                        "condition": cond,
                        "section": section.metadata.get("section_title", ""),
                        "policy": section.metadata.get("policy_name", ""),
                        "excerpt": section.page_content[:200],
                    })

        return {
            "covered": covered_items,
            "excluded": excluded_items,
            "section_matches": section_coverage_info,
            "all_coverage": coverage_list,
            "all_exclusions": exclusion_list,
        }

    def _analyze_patient_conditions(self, conditions: list, policy) -> list[dict]:
        """For each of the patient's pre-existing conditions, determine coverage status."""
        coverage_list = []
        try:
            coverage_list = json.loads(policy.coverage_details or "[]")
        except (json.JSONDecodeError, TypeError):
            pass

        exclusion_list = []
        try:
            exclusion_list = json.loads(policy.exclusions or "[]")
        except (json.JSONDecodeError, TypeError):
            pass

        results = []
        for cond in conditions:
            cond_lower = cond.lower()
            is_excluded = any(cond_lower in exc.lower() for exc in exclusion_list)
            is_covered = any(cond_lower in cov.lower() for cov in coverage_list)

            if is_excluded:
                status = "excluded"
            elif is_covered:
                status = "covered"
            else:
                status = "unknown"

            results.append({"condition": cond, "status": status})

        return results

    def generate_response(
        self,
        query: str,
        intents: list[str],
        coverage_assessment: dict,
        age_check: dict,
        policy,
        patient_details: dict = None,
        claims_context: list = None,
    ) -> tuple[str, list[str]]:
        parts = []
        follow_ups = []

        pd = patient_details or {}
        full_name = pd.get("full_name", "")
        first_name = full_name.split()[0] if full_name else ""
        age = pd.get("age")
        bmi = pd.get("bmi")
        is_smoker = pd.get("is_smoker", False)
        conditions = pd.get("conditions", [])

        greeting = f"Hi {first_name}!" if first_name else "Hello!"
        parts.append(f"{greeting} Here's what I found for you regarding **{policy.name}** ({policy.plan_type.title()} Plan):\n")

        # --- AGE ELIGIBILITY ---
        if "eligibility" in intents and age_check:
            if age_check.get("eligible") is True:
                parts.append(f"\n✅ **Age Eligibility:** {age_check['message']}")
            elif age_check.get("eligible") is False:
                parts.append(f"\n❌ **Age Eligibility:** {age_check['message']}")

        # --- PERSONALIZED PREMIUM ---
        if "premium" in intents or "eligibility" in intents or "general" in intents:
            calc_premium, premium_notes = _calculate_personalized_premium(policy, age, bmi, is_smoker)
            parts.append(f"\n**Your Estimated Monthly Premium: ${calc_premium:,.2f}**")
            if premium_notes:
                parts.append(f"*(Base: ${policy.monthly_premium_base:,.2f}, adjusted for: {', '.join(premium_notes)})*")
            else:
                parts.append(f"*(Base rate — no surcharges apply to your profile)*")
            parts.append(f"- Annual Deductible: ${policy.annual_deductible:,.2f}")
            parts.append(f"- Max Coverage Limit: ${policy.max_coverage_limit:,.2f}")
            parts.append(f"- Copay: {policy.copay_percentage:.0f}%")

        # --- DEDUCTIBLE (standalone query) ---
        elif "deductible" in intents:
            parts.append(f"\n**Your Cost Sharing:**")
            parts.append(f"- Annual Deductible: ${policy.annual_deductible:,.2f}")
            parts.append(f"- Copay: {policy.copay_percentage:.0f}%")
            parts.append(f"- Max Coverage: ${policy.max_coverage_limit:,.2f}")

        # --- PRE-EXISTING CONDITIONS ANALYSIS ---
        if conditions and ("eligibility" in intents or "coverage" in intents or "waiting_period" in intents or "general" in intents):
            condition_analysis = self._analyze_patient_conditions(conditions, policy)
            parts.append(f"\n**Your Pre-existing Conditions ({len(conditions)} on file):**")
            for item in condition_analysis:
                cond_title = item["condition"].title()
                if item["status"] == "covered":
                    parts.append(f"- **{cond_title}**: ✅ Covered (subject to {policy.pre_existing_waiting_months}-month waiting period)")
                elif item["status"] == "excluded":
                    parts.append(f"- **{cond_title}**: ❌ Not covered under this plan")
                else:
                    parts.append(f"- **{cond_title}**: ⚠️ Coverage unconfirmed — contact insurer")

        # --- SPECIFIC COVERAGE QUERY RESULTS ---
        if coverage_assessment.get("covered") or coverage_assessment.get("excluded"):
            if coverage_assessment.get("covered"):
                items = ", ".join(c.title() for c in coverage_assessment["covered"])
                parts.append(f"\n✅ **Covered:** {items}")
                parts.append(f"*(Waiting period: {policy.pre_existing_waiting_months} months for pre-existing conditions)*")

            if coverage_assessment.get("excluded"):
                items = ", ".join(c.title() for c in coverage_assessment["excluded"])
                parts.append(f"\n❌ **Not Covered:** {items}")

            if coverage_assessment.get("section_matches"):
                parts.append("\n**Relevant Policy Sections:**")
                seen_sections = set()
                for match in coverage_assessment["section_matches"][:3]:
                    key = match["section"]
                    if key not in seen_sections:
                        seen_sections.add(key)
                        parts.append(f"- *{match['section']}* ({match['policy']})")

        # --- COVERAGE OVERVIEW ---
        elif "coverage" in intents and not coverage_assessment.get("covered"):
            all_coverage = coverage_assessment.get("all_coverage", [])
            all_exclusions = coverage_assessment.get("all_exclusions", [])
            if all_coverage:
                parts.append(f"\n**Covered Services:** {', '.join(all_coverage[:8])}")
            if all_exclusions:
                parts.append(f"\n**Not Covered:** {', '.join(all_exclusions[:5])}")

        # --- EXCLUSIONS ---
        if "exclusion" in intents:
            all_exclusions = coverage_assessment.get("all_exclusions", [])
            if all_exclusions:
                parts.append(f"\n**Plan Exclusions:**")
                for exc in all_exclusions[:8]:
                    parts.append(f"- {exc}")

        # --- WAITING PERIOD ---
        if "waiting_period" in intents:
            parts.append(f"\n**Waiting Period:** This plan has a **{policy.pre_existing_waiting_months}-month** waiting period for pre-existing conditions.")
            if conditions:
                parts.append(f"This applies to your conditions: {', '.join(c.title() for c in conditions)}.")

        # --- CLAIMS CONTEXT ---
        if claims_context:
            pending = [c for c in claims_context if c["status"] == "pending"]
            approved = [c for c in claims_context if c["status"] == "approved"]
            rejected = [c for c in claims_context if c["status"] == "rejected"]

            if "claims" in intents or any(kw in query.lower() for kw in ["my claim", "claim status", "pending"]):
                parts.append(f"\n**Your Claims Summary:**")
                if pending:
                    parts.append(f"- **{len(pending)} Pending** — currently under review:")
                    for c in pending[:3]:
                        parts.append(f"  - Claim #{c['id']} ({c['claim_type'].title()}): ${c['amount_claimed']:,.2f} claimed")
                if approved:
                    total = sum(c.get("amount_approved") or 0 for c in approved)
                    parts.append(f"- **{len(approved)} Approved** — ${total:,.2f} total approved")
                if rejected:
                    parts.append(f"- **{len(rejected)} Rejected** on record")
                if not claims_context:
                    parts.append(f"- No claims filed yet")
                follow_ups.append("How do I check the details of a specific claim?")
            elif pending:
                parts.append(f"\n**Active Claims:** You have **{len(pending)} pending claim(s)** under review.")

        # --- PLAN COMPARISON ---
        if "comparison" in intents:
            parts.append(f"\n**Plan Comparison:** Use the Premium Estimator to compare costs across all available plans.")
            follow_ups.append("How does this plan compare to premium-tier plans?")

        # --- SMOKER & BMI NOTES (when not already shown in premium section) ---
        if is_smoker and policy.smoker_surcharge_pct > 0 and "premium" not in intents and "general" not in intents:
            parts.append(f"\n**Smoker Note:** A {policy.smoker_surcharge_pct:.0f}% premium surcharge applies to your profile.")
            follow_ups.append("How much would I save on premiums if I quit smoking?")

        if bmi and bmi > 30 and policy.bmi_surcharge_pct > 0 and "premium" not in intents and "general" not in intents:
            parts.append(f"\n**BMI Note:** Your BMI of {bmi:.1f} triggers a {policy.bmi_surcharge_pct:.0f}% surcharge on your base premium.")

        # --- GENERAL FALLBACK ---
        if "general" in intents and len(parts) <= 2:
            calc_premium, premium_notes = _calculate_personalized_premium(policy, age, bmi, is_smoker)
            parts.append(f"\n**Plan Overview:**")
            parts.append(f"- Your Monthly Premium: **${calc_premium:,.2f}**")
            if premium_notes:
                parts.append(f"  *(adjusted for {', '.join(premium_notes)})*")
            parts.append(f"- Annual Deductible: ${policy.annual_deductible:,.2f}")
            parts.append(f"- Max Coverage: ${policy.max_coverage_limit:,.2f}")
            parts.append(f"- Copay: {policy.copay_percentage:.0f}%")
            parts.append(f"- Eligible Age Range: {policy.age_min}–{policy.age_max}")

            all_coverage = coverage_assessment.get("all_coverage", [])
            if all_coverage:
                parts.append(f"\n**Covered Services:** {', '.join(all_coverage[:8])}")

            all_exclusions = coverage_assessment.get("all_exclusions", [])
            if all_exclusions:
                parts.append(f"\n**Exclusions:** {', '.join(all_exclusions[:5])}")

            if conditions:
                condition_analysis = self._analyze_patient_conditions(conditions, policy)
                parts.append(f"\n**Your Conditions:**")
                for item in condition_analysis:
                    cond_title = item["condition"].title()
                    if item["status"] == "covered":
                        parts.append(f"- {cond_title}: ✅ Covered (after {policy.pre_existing_waiting_months}-month wait)")
                    elif item["status"] == "excluded":
                        parts.append(f"- {cond_title}: ❌ Excluded")
                    else:
                        parts.append(f"- {cond_title}: ⚠️ Verify with insurer")

        # --- SMART FOLLOW-UPS BASED ON PATIENT PROFILE ---
        if not follow_ups:
            if conditions:
                follow_ups.append(f"Is my {conditions[0].title()} treatment fully covered?")
                if len(conditions) > 1:
                    follow_ups.append(f"How long is the waiting period for {conditions[1].title()}?")
            if is_smoker:
                follow_ups.append("How does smoking affect my eligibility and premium?")
            if claims_context and any(c["status"] == "pending" for c in claims_context):
                follow_ups.append("What's the status of my pending claims?")
            if "premium" not in intents:
                follow_ups.append("What is my personalized monthly premium?")
            follow_ups.append("How do I submit a new claim?")

        # Deduplicate and cap
        seen_fu = set()
        unique_follow_ups = []
        for fu in follow_ups:
            if fu not in seen_fu:
                seen_fu.add(fu)
                unique_follow_ups.append(fu)

        return "\n".join(parts), unique_follow_ups[:4]
