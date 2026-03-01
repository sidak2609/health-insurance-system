from app.models.enums import RiskLevel

HIGH_RISK_CONDITIONS = [
    "diabetes", "heart disease", "cancer", "kidney disease",
    "liver disease", "stroke", "hypertension", "copd",
]


def calculate_risk_score(
    age: int = None,
    bmi: float = None,
    is_smoker: bool = False,
    conditions: list[str] = None,
    claim_amount: float = 0,
    policy_max: float = 1,
) -> tuple[float, str]:
    score = 0.0
    conditions = conditions or []

    # Age factor
    if age:
        if age >= 60:
            score += 0.20
        elif age >= 50:
            score += 0.15
        elif age >= 40:
            score += 0.10

    # BMI factor
    if bmi:
        if bmi >= 35:
            score += 0.20
        elif bmi >= 30:
            score += 0.15
        elif bmi >= 25:
            score += 0.10
        elif bmi < 18.5:
            score += 0.05

    # Smoker factor
    if is_smoker:
        score += 0.15

    # Pre-existing conditions
    condition_score = 0.0
    for cond in conditions:
        if cond.lower() in HIGH_RISK_CONDITIONS:
            condition_score += 0.10
    score += min(condition_score, 0.30)

    # Claim ratio
    if policy_max > 0 and claim_amount > 0:
        ratio = claim_amount / policy_max
        if ratio > 0.5:
            score += 0.15
        elif ratio > 0.3:
            score += 0.10
        elif ratio > 0.1:
            score += 0.08

    score = min(score, 1.0)

    if score >= 0.6:
        level = RiskLevel.high
    elif score >= 0.3:
        level = RiskLevel.medium
    else:
        level = RiskLevel.low

    return round(score, 2), level.value
