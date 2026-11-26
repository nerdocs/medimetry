from dataclasses import dataclass
from enum import Enum


class GenevaRiskLevel(Enum):
    """Geneva score clinical probability categories for pulmonary embolism."""

    LOW = "low"
    INTERMEDIATE = "intermediate"
    HIGH = "high"


@dataclass
class PERCResult:
    """PERC rule result: number of positive criteria; ``positive`` is True if any criterion is met."""

    positive_criteria: int
    positive: bool


def _validate_geneva_inputs(age: int, heart_rate: int) -> None:
    if age <= 0:
        raise ValueError(f"Age must be positive: {age}")
    if heart_rate <= 0 or heart_rate > 300:
        raise ValueError(f"Heart rate must be between 1 and 300 bpm: {heart_rate}")


def geneva_simplified_score(
    age: int,
    heart_rate: int,
    previous_pe_dvt: bool = False,
    recent_surgery_or_fracture: bool = False,
    hemoptysis: bool = False,
    active_cancer: bool = False,
    unilateral_leg_pain: bool = False,
    leg_pain_on_palpation_and_edema: bool = False,
) -> int:
    """
    Calculate the Simplified Revised Geneva Score for clinical probability of pulmonary embolism.

    All items score 1 point except heart rate >= 95 bpm (2 points). The probability category
    is a separate step: ``geneva_simplified_category``.

    References:
        Klok FA, et al. Simplification of the revised Geneva score for assessing clinical
        probability of pulmonary embolism. Arch Intern Med. 2008;168(19):2131-2136.
        doi:10.1001/archinte.168.19.2131

    Args:
        age (int): Age in years (> 65 scores 1 point)
        heart_rate (int): Heart rate in bpm (75-94: 1 point, >= 95: 2 points)
        previous_pe_dvt (bool): Previous PE or DVT
        recent_surgery_or_fracture (bool): Surgery or fracture within the last month
        hemoptysis (bool): Hemoptysis
        active_cancer (bool): Active malignant condition
        unilateral_leg_pain (bool): Unilateral lower limb pain
        leg_pain_on_palpation_and_edema (bool): Pain on lower limb deep venous palpation
            *and* unilateral edema (one combined item)

    Returns:
        int: Total points (0-9)

    Raises:
        ValueError: If age or heart rate are out of range

    >>> geneva_simplified_score(age=70, heart_rate=100, previous_pe_dvt=True)
    4
    """
    _validate_geneva_inputs(age, heart_rate)

    score = 0
    if age > 65:
        score += 1
    if 75 <= heart_rate <= 94:
        score += 1
    elif heart_rate >= 95:
        score += 2
    for item in (
        previous_pe_dvt,
        recent_surgery_or_fracture,
        hemoptysis,
        active_cancer,
        unilateral_leg_pain,
        leg_pain_on_palpation_and_edema,
    ):
        if item:
            score += 1

    return score


def _check_geneva_score(score: int, maximum: int) -> None:
    if not isinstance(score, int) or isinstance(score, bool):
        raise TypeError(f"Geneva score must be an int: {score!r}")
    if not 0 <= score <= maximum:
        raise ValueError(f"Geneva score must be between 0 and {maximum}: {score}")


def geneva_simplified_category(score: int) -> GenevaRiskLevel:
    """
    Return the three-level clinical probability category of a Simplified Revised Geneva Score.

    Three-level classification as published: 0-1 low, 2-4 intermediate, >= 5 high.

    References:
        Klok FA, et al. Simplification of the revised Geneva score for assessing clinical
        probability of pulmonary embolism. Arch Intern Med. 2008;168(19):2131-2136.
        doi:10.1001/archinte.168.19.2131

    Args:
        score (int): Simplified Revised Geneva Score (0-9), e.g. from ``geneva_simplified_score``

    Returns:
        GenevaRiskLevel: Probability category

    Raises:
        TypeError: If score is not an int
        ValueError: If score is outside 0-9

    >>> geneva_simplified_category(4)
    <GenevaRiskLevel.INTERMEDIATE: 'intermediate'>
    """
    _check_geneva_score(score, 9)
    if score <= 1:
        return GenevaRiskLevel.LOW
    if score <= 4:
        return GenevaRiskLevel.INTERMEDIATE
    return GenevaRiskLevel.HIGH


def geneva_revised_score(
    age: int,
    heart_rate: int,
    previous_pe_dvt: bool = False,
    recent_surgery_or_fracture: bool = False,
    hemoptysis: bool = False,
    active_cancer: bool = False,
    unilateral_leg_pain: bool = False,
    leg_pain_on_palpation_and_edema: bool = False,
) -> int:
    """
    Calculate the Revised Geneva Score for clinical probability of pulmonary embolism.

    The probability category is a separate step: ``geneva_revised_category``.

    References:
        Le Gal G, et al. Prediction of pulmonary embolism in the emergency department:
        the revised Geneva score. Ann Intern Med. 2006;144(3):165-171.
        doi:10.7326/0003-4819-144-3-200602070-00004

    Args:
        age (int): Age in years (> 65 scores 1 point)
        heart_rate (int): Heart rate in bpm (75-94: 3 points, >= 95: 5 points)
        previous_pe_dvt (bool): Previous PE or DVT (3 points)
        recent_surgery_or_fracture (bool): Surgery or fracture within the last month (2 points)
        hemoptysis (bool): Hemoptysis (2 points)
        active_cancer (bool): Active malignant condition (2 points)
        unilateral_leg_pain (bool): Unilateral lower limb pain (3 points)
        leg_pain_on_palpation_and_edema (bool): Pain on lower limb deep venous palpation
            *and* unilateral edema (one combined item, 4 points)

    Returns:
        int: Total points (0-22)

    Raises:
        ValueError: If age or heart rate are out of range

    >>> geneva_revised_score(age=70, heart_rate=100, previous_pe_dvt=True)
    9
    """
    _validate_geneva_inputs(age, heart_rate)

    score = 0
    if age > 65:
        score += 1
    if 75 <= heart_rate <= 94:
        score += 3
    elif heart_rate >= 95:
        score += 5
    if previous_pe_dvt:
        score += 3
    if recent_surgery_or_fracture:
        score += 2
    if hemoptysis:
        score += 2
    if active_cancer:
        score += 2
    if unilateral_leg_pain:
        score += 3
    if leg_pain_on_palpation_and_edema:
        score += 4

    return score


def geneva_revised_category(score: int) -> GenevaRiskLevel:
    """
    Return the three-level clinical probability category of a Revised Geneva Score.

    Three-level classification as published: 0-3 low, 4-10 intermediate, >= 11 high.

    References:
        Le Gal G, et al. Prediction of pulmonary embolism in the emergency department:
        the revised Geneva score. Ann Intern Med. 2006;144(3):165-171.
        doi:10.7326/0003-4819-144-3-200602070-00004

    Args:
        score (int): Revised Geneva Score (0-22), e.g. from ``geneva_revised_score``

    Returns:
        GenevaRiskLevel: Probability category

    Raises:
        TypeError: If score is not an int
        ValueError: If score is outside 0-22

    >>> geneva_revised_category(9)
    <GenevaRiskLevel.INTERMEDIATE: 'intermediate'>
    """
    _check_geneva_score(score, 22)
    if score <= 3:
        return GenevaRiskLevel.LOW
    if score <= 10:
        return GenevaRiskLevel.INTERMEDIATE
    return GenevaRiskLevel.HIGH


def perc_rule(
    age: int,
    heart_rate: int,
    oxygen_saturation: float,
    unilateral_leg_swelling: bool = False,
    hemoptysis: bool = False,
    recent_surgery_trauma: bool = False,
    prior_pe_dvt: bool = False,
    exogenous_estrogen: bool = False,
) -> PERCResult:
    """
    Evaluate the PERC (Pulmonary Embolism Rule-out Criteria) rule.

    The rule counts eight criteria; it is "negative" only if none of them is met.
    Interpretation of a negative or positive result is outside the scope of this
    function.

    References:
        Kline JA, et al. Clinical criteria to prevent unnecessary diagnostic testing in
        emergency department patients with suspected pulmonary embolism.
        J Thromb Haemost. 2004;2(8):1247-1255. doi:10.1111/j.1538-7836.2004.00790.x

    Args:
        age (int): Age in years (criterion: >= 50)
        heart_rate (int): Heart rate in bpm (criterion: >= 100)
        oxygen_saturation (float): Oxygen saturation on room air in percent (criterion: < 95)
        unilateral_leg_swelling (bool): Unilateral leg swelling
        hemoptysis (bool): Hemoptysis
        recent_surgery_trauma (bool): Surgery or trauma requiring hospitalization within 4 weeks
        prior_pe_dvt (bool): Prior PE or DVT
        exogenous_estrogen (bool): Exogenous estrogen use (oral contraceptives, hormone replacement)

    Returns:
        PERCResult: Number of positive criteria and whether any criterion is positive

    Raises:
        ValueError: If age, heart rate, or oxygen saturation are invalid

    >>> perc_rule(age=30, heart_rate=80, oxygen_saturation=98.0)
    PERCResult(positive_criteria=0, positive=False)
    """
    if age <= 0:
        raise ValueError(f"Age must be positive: {age}")
    if heart_rate <= 0 or heart_rate > 300:
        raise ValueError(f"Heart rate must be between 1 and 300 bpm: {heart_rate}")
    if oxygen_saturation <= 0 or oxygen_saturation > 100:
        raise ValueError(f"Oxygen saturation must be between 0 and 100%: {oxygen_saturation}")

    criteria = (
        age >= 50,
        heart_rate >= 100,
        oxygen_saturation < 95.0,
        unilateral_leg_swelling,
        hemoptysis,
        recent_surgery_trauma,
        prior_pe_dvt,
        exogenous_estrogen,
    )
    criteria_count = sum(1 for c in criteria if c)

    return PERCResult(positive_criteria=criteria_count, positive=criteria_count > 0)
