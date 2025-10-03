from medimetry.constants import EthnicalRace
from medimetry.constants import Sex


def cockcroft_gault(age: int, weight: float, creatinine: float, sex: Sex, height: float | None = None) -> int:
    """
    Calculate creatinine clearance using Cockcroft-Gault formula.

    Args:
        age (int): Age in years
        weight (float): Weight in kg
        creatinine (float): Serum creatinine in mg/dl
        sex (str): Sex ("male" or "female")
        height (float, optional): Height in cm (not used in standard formula)

    Returns:
        float: Creatinine clearance in mL/min
    """
    assert weight > 0, "Weight must be positive"
    assert weight < 400, "Weight must be less than 400 kg"
    assert age > 0, "Age must be positive"
    assert creatinine >= 0, "Creatinine must be non-negative"
    assert sex in (Sex.MALE, Sex.FEMALE), "Sex must be 'm' or 'f'"
    assert height is None or (0 < height < 150), "Height must be positive and less than 150 cm"

    # Base calculation: ((140 - age) * weight) / (72 * creatinine)
    clearance = ((140 - age) * weight) / (72 * creatinine)

    # Apply sex correction factor
    if sex == Sex.FEMALE:
        clearance *= 0.85

    return round(clearance)


def mdrd(creatinine: float, age: int, sex: Sex, race: EthnicalRace = EthnicalRace.OTHER) -> float:
    """
    Calculate eGFR using MDRD (Modification of Diet in Renal Disease) formula.

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (int): Age in years
        sex (str): Sex ("m" or "f")
        race (str): Race ("african_american" or "other")

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    assert creatinine > 0, "Creatinine must be positive"
    assert age > 0, "Age must be positive"
    assert sex in (Sex.MALE, Sex.FEMALE), "Sex must be Sex.MALE|Sex.FEMALE"

    # Base MDRD formula: 175 x (creatinine)^-1.154 x (age)^-0.203
    egfr = 175 * (creatinine**-1.154) * (age**-0.203)

    # Apply sex correction factor
    if sex == Sex.FEMALE:
        egfr *= 0.742

    # Apply race correction factor
    if race == EthnicalRace.AFRICAN_AMERICAN:
        egfr *= 1.212

    return egfr


def ckd_epi(creatinine: float, age: int, sex: Sex, race: EthnicalRace = EthnicalRace.OTHER) -> float:
    """
    Calculate eGFR using CKD-EPI (Chronic Kidney Disease Epidemiology Collaboration) formula.

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (int): Age in years
        sex (Sex): Sex (Sex.MALE or Sex.FEMALE)
        race (EthnicalRace): Race (EthnicalRace.AFRICAN_AMERICAN or EthnicalRace.OTHER)

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    assert creatinine > 0, "Creatinine must be positive"
    assert age > 0, "Age must be positive"
    assert sex in (Sex.MALE, Sex.FEMALE), "Sex must be Sex.MALE|Sex.FEMALE"

    # Define kappa and alpha based on sex
    if sex == Sex.FEMALE:
        kappa = 0.7
        alpha = -0.329
        sex_factor = 1.018
    else:
        kappa = 0.9
        alpha = -0.411
        sex_factor = 1.0

    # Calculate min and max terms
    cr_kappa_ratio = creatinine / kappa
    min_term = min(cr_kappa_ratio, 1.0) ** alpha
    max_term = max(cr_kappa_ratio, 1.0) ** -1.209

    # Base CKD-EPI formula
    egfr = 141 * min_term * max_term * (0.993**age) * sex_factor

    # Apply race correction factor
    if race == EthnicalRace.AFRICAN_AMERICAN:
        egfr *= 1.159

    return egfr
