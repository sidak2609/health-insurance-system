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
    "eligibility": ["eligible", "eligibility", "qualify", "qualification", "can i", "am i"],
    "coverage": ["cover", "coverage", "covered", "include", "included", "what does", "does it cover"],
    "exclusion": ["exclude", "exclusion", "not covered", "excluded", "what is not", "what isn't"],
    "premium": ["premium", "cost", "price", "how much", "monthly", "payment", "afford"],
    "deductible": ["deductible", "out of pocket", "copay", "co-pay"],
    "claims": ["claim", "file", "submit", "reimbursement", "reimburse"],
    "waiting_period": ["waiting period", "pre-existing", "waiting", "how long"],
    "comparison": ["compare", "comparison", "difference", "better", "vs", "versus", "which plan"],
}


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
        query_lower = query.lower()

        # Check mentioned conditions against coverage/exclusions
        for cond in conditions:
            cond_lower = cond.lower()
            is_excluded = any(cond_lower in exc.lower() for exc in exclusion_list)
            is_covered = any(cond_lower in cov.lower() for cov in coverage_list)

            if is_excluded:
                excluded_items.append(cond)
            elif is_covered:
                covered_items.append(cond)

        # Also scan retrieved sections for coverage info
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

    def generate_response(
        self,
        query: str,
        intents: list[str],
        coverage_assessment: dict,
        age_check: dict,
        policy,
        patient_details: dict = None,
    ) -> tuple[str, list[str]]:
        parts = []
        follow_ups = []

        # Greeting
        parts.append(f"Based on your query about **{policy.name}** ({policy.plan_type.title()} Plan):\n")

        # Age eligibility
        if "eligibility" in intents and age_check:
            if age_check["eligible"] is True:
                parts.append(f"**Age Eligibility:** {age_check['message']}")
            elif age_check["eligible"] is False:
                parts.append(f"**Age Eligibility:** {age_check['message']}")
            else:
                parts.append(f"**Age Eligibility:** {age_check['message']}")

        # Coverage results
        if "coverage" in intents or "exclusion" in intents or coverage_assessment.get("covered") or coverage_assessment.get("excluded"):
            if coverage_assessment.get("covered"):
                items = ", ".join(coverage_assessment["covered"])
                parts.append(f"\n**Covered:** {items} are included in this plan's coverage.")

            if coverage_assessment.get("excluded"):
                items = ", ".join(coverage_assessment["excluded"])
                parts.append(f"\n**Not Covered:** {items} are listed as exclusions for this plan.")

            if coverage_assessment.get("section_matches"):
                parts.append("\n**Relevant Policy Sections:**")
                for match in coverage_assessment["section_matches"][:3]:
                    parts.append(f"- *{match['section']}* ({match['policy']}): {match['excerpt'][:150]}...")

        # Premium info
        if "premium" in intents:
            parts.append(f"\n**Premium Information:**")
            parts.append(f"- Base Monthly Premium: ${policy.monthly_premium_base:,.2f}")
            parts.append(f"- Annual Deductible: ${policy.annual_deductible:,.2f}")
            parts.append(f"- Maximum Coverage: ${policy.max_coverage_limit:,.2f}")
            parts.append(f"- Copay: {policy.copay_percentage}%")
            if policy.smoker_surcharge_pct > 0:
                parts.append(f"- Smoker Surcharge: {policy.smoker_surcharge_pct}%")
            follow_ups.append("Would you like a personalized premium estimate?")

        # Deductible info
        if "deductible" in intents:
            parts.append(f"\n**Cost Sharing:**")
            parts.append(f"- Annual Deductible: ${policy.annual_deductible:,.2f}")
            parts.append(f"- Copay Percentage: {policy.copay_percentage}%")

        # Claims info
        if "claims" in intents:
            parts.append(f"\n**Claims Process:** You can submit claims through the claims portal. "
                        f"Each claim will be assessed based on your policy coverage and risk profile.")
            follow_ups.append("Would you like to submit a new claim?")

        # Waiting period
        if "waiting_period" in intents:
            parts.append(f"\n**Waiting Period:** This plan has a {policy.pre_existing_waiting_months}-month "
                        f"waiting period for pre-existing conditions.")

        # Comparison
        if "comparison" in intents:
            parts.append(f"\n**Plan Comparison:** Use the Premium Estimator to compare costs across all available plans.")
            follow_ups.append("Would you like to compare this plan with other available plans?")

        # General fallback
        if "general" in intents and len(parts) == 1:
            parts.append(f"\n**Plan Overview:**")
            parts.append(f"- Monthly Premium: ${policy.monthly_premium_base:,.2f}")
            parts.append(f"- Deductible: ${policy.annual_deductible:,.2f}")
            parts.append(f"- Max Coverage: ${policy.max_coverage_limit:,.2f}")
            parts.append(f"- Copay: {policy.copay_percentage}%")
            parts.append(f"- Age Range: {policy.age_min}-{policy.age_max}")

            coverage = coverage_assessment.get("all_coverage", [])
            if coverage:
                parts.append(f"\n**Covered Services:** {', '.join(coverage[:8])}")

            exclusions = coverage_assessment.get("all_exclusions", [])
            if exclusions:
                parts.append(f"\n**Exclusions:** {', '.join(exclusions[:5])}")

        # Patient-specific notes
        if patient_details:
            smoker = patient_details.get("is_smoker", False)
            conditions = patient_details.get("conditions", [])
            if smoker and policy.smoker_surcharge_pct > 0:
                parts.append(f"\n**Note:** As a smoker, a {policy.smoker_surcharge_pct}% surcharge applies to your premium.")
            if conditions:
                parts.append(f"\n**Note:** You have listed pre-existing conditions: {', '.join(conditions)}. "
                           f"A {policy.pre_existing_waiting_months}-month waiting period may apply.")

        # Default follow-ups
        if not follow_ups:
            follow_ups = [
                "What specific conditions would you like to check coverage for?",
                "Would you like to see the premium breakdown for this plan?",
                "Would you like to compare this with other available plans?",
            ]

        return "\n".join(parts), follow_ups
