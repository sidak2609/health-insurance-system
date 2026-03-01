from app.db.models import Policy


def estimate_premium(
    policy: Policy,
    age: int,
    bmi: float,
    is_smoker: bool = False,
    conditions: list[str] = None,
) -> dict:
    conditions = conditions or []
    base = policy.monthly_premium_base

    # Age adjustment: +2% per year over 30
    age_adj = 0.0
    if age > 30:
        age_adj = base * (age - 30) * 0.02

    # BMI surcharge
    bmi_adj = 0.0
    if bmi >= 30 and policy.bmi_surcharge_pct > 0:
        bmi_adj = base * (policy.bmi_surcharge_pct / 100)

    # Smoker surcharge
    smoker_adj = 0.0
    if is_smoker and policy.smoker_surcharge_pct > 0:
        smoker_adj = base * (policy.smoker_surcharge_pct / 100)

    # Condition surcharge: +5% per condition, cap 25%
    condition_adj = 0.0
    if conditions:
        pct = min(len(conditions) * 5, 25)
        condition_adj = base * (pct / 100)

    final = base + age_adj + bmi_adj + smoker_adj + condition_adj

    return {
        "policy_id": policy.id,
        "policy_name": policy.name,
        "plan_type": policy.plan_type,
        "base_premium": round(base, 2),
        "age_adjustment": round(age_adj, 2),
        "bmi_adjustment": round(bmi_adj, 2),
        "smoker_adjustment": round(smoker_adj, 2),
        "condition_adjustment": round(condition_adj, 2),
        "final_monthly_premium": round(final, 2),
        "annual_deductible": policy.annual_deductible,
        "max_coverage": policy.max_coverage_limit,
        "copay_percentage": policy.copay_percentage,
    }
