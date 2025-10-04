from dataclasses import dataclass
from enum import Enum
from gettext import gettext as _


class GenevaRiskLevel(Enum):
    """Geneva score risk levels for pulmonary embolism."""

    LOW = _("Low")
    INTERMEDIATE = _("Intermediate")
    HIGH = _("High")


@dataclass
class GenevaScore:
    """Geneva score result for pulmonary embolism risk assessment."""

    score: int
    risk_level: GenevaRiskLevel
    pe_probability: str


@dataclass
class PERCResult:
    """PERC rule result for pulmonary embolism rule-out."""

    positive_criteria: int
    positive: bool
    recommendation: str

    def __bool__(self) -> bool:
        return self.positive


def geneva_score(
    age: int,
    previous_pe_dvt: bool = False,
    heart_rate_over_100: bool = False,
    recent_surgery: bool = False,
    hemoptysis: bool = False,
    active_cancer: bool = False,
    unilateral_leg_pain: bool = False,
    unilateral_leg_edema: bool = False,
    pain_on_palpation: bool = False,
) -> GenevaScore:
    """
    Calculate Geneva score for pulmonary embolism risk assessment.

    The Geneva score is a clinical prediction rule used to estimate the
    probability of pulmonary embolism in patients with suspected PE.
    This is the revised simplified Geneva Score version (Klok et al., 2008)

    Args:
        age (int): Patient age in years
        previous_pe_dvt (bool): Previous PE or DVT history
        heart_rate_over_100 (bool): Heart rate > 100 bpm
        recent_surgery (bool): Surgery or fracture within 1 month
        hemoptysis (bool): Hemoptysis present
        active_cancer (bool): Active cancer (treatment ongoing, within 6 months, or palliative)
        unilateral_leg_pain (bool): Unilateral lower limb pain
        unilateral_leg_edema (bool): Unilateral lower limb edema and superficial venous dilatation
        pain_on_palpation (bool): Pain on lower limb deep venous palpation

    Returns:
        GenevaScore: Score result with risk level and probability

    Raises:
        ValueError: If age is not positive
    """
    if age <= 0:
        raise ValueError("Age must be positive")

    score = 0

    # Age scoring
    if 60 <= age <= 79:
        score += 1
    elif age >= 80:
        score += 2

    # Clinical factors (each worth 1 point)
    if previous_pe_dvt:
        score += 1
    if heart_rate_over_100:
        score += 1
    if recent_surgery:
        score += 1
    if hemoptysis:
        score += 1
    if active_cancer:
        score += 1
    if unilateral_leg_pain:
        score += 1
    if unilateral_leg_edema:
        score += 1
    if pain_on_palpation:
        score += 1

    # Determine risk level and probability
    if score <= 3:
        risk_level = GenevaRiskLevel.LOW
        probability = "8%"
    elif score <= 8:
        risk_level = GenevaRiskLevel.INTERMEDIATE
        probability = "28%"
    else:
        risk_level = GenevaRiskLevel.HIGH
        probability = "74%"

    return GenevaScore(score=score, risk_level=risk_level, pe_probability=probability)


def geneva_revised_score(
    age: int,
    previous_pe_dvt: bool = False,
    heart_rate: int | None = None,
    recent_surgery: bool = False,
    hemoptysis: bool = False,
    active_cancer: bool = False,
    unilateral_leg_pain: bool = False,
    unilateral_leg_edema: bool = False,
    pain_on_palpation: bool = False,
) -> GenevaScore:
    """
    Calculate Revised Geneva score for pulmonary embolism risk assessment.

    This Revised Geneva score (Le Gal et al., 2006) uses more specific heart rate
    thresholds compared to the original Geneva score.

    Args:
        age (int): Patient age in years
        previous_pe_dvt (bool): Previous PE or DVT history
        heart_rate (Optional[int]): Heart rate in bpm (if None, assumed normal)
        recent_surgery (bool): Surgery or fracture within 1 month
        hemoptysis (bool): Hemoptysis present
        active_cancer (bool): Active cancer
        unilateral_leg_pain (bool): Unilateral lower limb pain
        unilateral_leg_edema (bool): Unilateral lower limb edema
        pain_on_palpation (bool): Pain on lower limb deep venous palpation

    Returns:
        GenevaScore: Score result with risk level and probability

    Raises:
        ValueError: If age is not positive or heart rate is invalid
    """
    if age <= 0:
        raise ValueError("Age must be positive")
    if heart_rate is not None and (heart_rate <= 0 or heart_rate > 300):
        raise ValueError("Heart rate must be between 1 and 300 bpm")

    score = 0

    # Age scoring
    if age >= 65:
        score += 1

    # Heart rate scoring (more specific than original)
    if heart_rate is not None:
        if 75 <= heart_rate <= 94:
            score += 3
        elif heart_rate >= 95:
            score += 5

    # Clinical factors
    if previous_pe_dvt:
        score += 3
    if recent_surgery:
        score += 2
    if hemoptysis:
        score += 2
    if active_cancer:
        score += 2
    if unilateral_leg_pain:
        score += 3
    if unilateral_leg_edema:
        score += 4
    if pain_on_palpation:
        score += 4

    # Determine risk level and probability
    if score <= 3:
        risk_level = GenevaRiskLevel.LOW
        probability = "8%"
    elif score <= 10:
        risk_level = GenevaRiskLevel.INTERMEDIATE
        probability = "28%"
    else:
        risk_level = GenevaRiskLevel.HIGH
        probability = "74%"

    return GenevaScore(score=score, risk_level=risk_level, pe_probability=probability)


def perc_rule(
    age: int,
    heart_rate: int,
    oxygen_saturation: float,
    unilateral_leg_swelling: bool = False,
    hemoptysis: bool = False,
    recent_surgery_trauma: bool = False,
    prior_pe_dvt: bool = False,
    hormone_use: bool = False,
) -> PERCResult:
    """
    Calculate PERC (Pulmonary Embolism Rule-out Criteria) rule.

    The PERC rule is used to rule out pulmonary embolism in low-risk patients
    without further testing. If all 8 criteria are negative (PERC negative),
    PE can be ruled out without D-dimer or imaging in low-risk patients.

    Args:
        age (int): Patient age in years
        heart_rate (int): Heart rate in bpm
        oxygen_saturation (float): Oxygen saturation as percentage (e.g., 98.5)
        unilateral_leg_swelling (bool): Unilateral leg swelling present
        hemoptysis (bool): Hemoptysis present
        recent_surgery_trauma (bool): Recent surgery or trauma (within 4 weeks)
        prior_pe_dvt (bool): Prior history of PE or DVT
        hormone_use (bool): Hormone use (oral contraceptives, hormone replacement, pregnancy)

    Returns:
        PERCResult: Result with number of positive criteria and recommendation

    Raises:
        ValueError: If age, heart rate, or oxygen saturation are invalid
    """
    if age <= 0:
        raise ValueError("Age must be positive")
    if heart_rate <= 0 or heart_rate > 300:
        raise ValueError("Heart rate must be between 1 and 300 bpm")
    if oxygen_saturation <= 0 or oxygen_saturation > 100:
        raise ValueError("Oxygen saturation must be between 0 and 100%")

    criteria_count = 0

    # PERC criteria (each criterion adds 1 if positive)
    if age >= 50:
        criteria_count += 1
    if heart_rate >= 100:
        criteria_count += 1
    if oxygen_saturation < 95.0:
        criteria_count += 1
    if unilateral_leg_swelling:
        criteria_count += 1
    if hemoptysis:
        criteria_count += 1
    if recent_surgery_trauma:
        criteria_count += 1
    if prior_pe_dvt:
        criteria_count += 1
    if hormone_use:
        criteria_count += 1

    # PERC is positive if any criteria are positive
    perc_positive = criteria_count > 0

    if not perc_positive:
        recommendation = _("PERC negative - PE can be ruled out without further testing in low-risk patients")
    else:
        recommendation = _("PERC positive ({criteria_count} criteria) - Further evaluation needed").format(criteria_count=criteria_count)

    return PERCResult(
        positive_criteria=criteria_count,
        positive=perc_positive,
        recommendation=recommendation,
    )
