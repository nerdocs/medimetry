from medimetry import Sex


def mean_arterial_pressure(systolic: int, diastolic: int) -> float:
    """
    Calculate mean arterial pressure (MAP) from systolic and diastolic blood pressure.

    Args:
        systolic (int): Systolic blood pressure in mm Hg
        diastolic (int): Diastolic blood pressure in mm Hg

    Returns:
        float: Mean arterial pressure in mm Hg
    Raises:
        ValueError: If either systolic or diastolic pressure is negative or diastolic
        is greater than systolic.
    """
    if systolic <= 0:
        raise ValueError("Systolic pressure must be non-negative")
    if diastolic <= 0:
        raise ValueError("Diastolic pressure must be non-negative")
    if diastolic >= systolic:
        raise ValueError("Diastolic pressure must be greater than systolic pressure. ")

    return round((2 * diastolic + systolic) / 3, 1)


def chads_vasc_score(
    age: int,
    sex: Sex,
    chf: bool = False,
    hypertension: bool = False,
    stroke_vascular_history: bool = False,
    diabetes: bool = False,
    vascular_disease: bool = False,
) -> int:
    """
    Calculate CHA2DS2-VASc score for stroke risk assessment in atrial fibrillation.

    Args:
        age (int): Age in years
        sex (Sex): Sex (Sex.MALE or Sex.FEMALE)
        chf (bool): Congestive heart failure/LV dysfunction
        hypertension (bool): Hypertension
        stroke_vascular_history (bool): Stroke/TIA/thromboembolism history
        diabetes (bool): Diabetes mellitus
        vascular_disease (bool): Vascular disease (prior MI, PAD, or aortic plaque)

    Returns:
        int: CHA2DS2-VASc score (0-9)
    """
    if age <= 0:
        raise ValueError("Age must be non-negative")
    assert sex in (Sex.MALE, Sex.FEMALE), "Sex must be Sex.MALE or Sex.FEMALE"

    score = 0

    # Age scoring
    if age >= 75:
        score += 2
    elif age >= 65:
        score += 1

    # Sex category (female)
    if sex == Sex.FEMALE:
        score += 1

    # Clinical factors (1 point each)
    if chf:
        score += 1
    if hypertension:
        score += 1
    if diabetes:
        score += 1
    if vascular_disease:
        score += 1

    # Stroke/vascular history (2 points)
    if stroke_vascular_history:
        score += 2

    return score
