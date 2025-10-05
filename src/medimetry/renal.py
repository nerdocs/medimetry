from gettext import gettext as _

from medimetry.constants import EthnicalRace
from medimetry.constants import Gender


def acr(albumin: float, creatinine: float):
    """
    Calculate Albumin-to-Creatinine Ratio (ACR) using the formula from the MDRD.

    Args:
        albumin (float): Albumin concentration in mg/dl
        creatinine (float): Serum creatinine in mg/dl

    Returns:
        float: Albumin-to-Creatinine Ratio
    """
    assert albumin >= 0, "Albumin must not be negative"
    assert creatinine > 0, "Creatinine must not positive"

    return albumin / creatinine


def cockcroft_gault(
    age: int,
    weight: float,
    creatinine: float,
    gender: Gender,
) -> int:
    """
    Calculate creatinine clearance using Cockcroft-Gault formula.

    Note: This formula has been replaced by the CDK-EPI formula for accuracy.
    It is still occasionally used, but it is no longer recommended in the
    literature. Its disadvantages include the fact that it was derived from an
    evaluation of only 249 participants, requires laboratories to know the patient's
    body weight, and does not normalize the result to body surface area.

    Args:
        age (int): Age in years
        weight (float): Weight in kg
        creatinine (float): Serum creatinine in mg/dl
        gender (str): Gender (MALE or FEMALE)

    Returns:
        float: Creatinine clearance in mL/min
    """
    assert weight > 0, "Weight must be positive"
    assert weight < 400, "Weight must be less than 400 kg"
    assert age > 0, "Age must be positive"
    assert creatinine >= 0, "Creatinine must not be negative"
    assert isinstance(gender, Gender), "gender must be a Gender instance"

    if float(creatinine) == 0.0:
        raise ValueError("Creatinine must be non-zero")
    # Base calculation: ((140 - age) * weight) / (72 * creatinine)
    clearance = ((140 - age) * weight) / (72 * creatinine)

    # Apply sex correction factor
    if gender == Gender.FEMALE:
        clearance *= 0.85

    return round(clearance)


def mdrd(creatinine: float, age: int, gender: Gender, race: EthnicalRace = EthnicalRace.OTHER) -> float:
    """
    Calculate eGFR using MDRD (Modification of Diet in Renal Disease) formula.

    Note: This formula has been replaced by the CDK-EPI formula for accuracy.

    eGFR=175 x (creatinine)^-1.154 x (age)^-0.203 x (0.742 if female) x (1.212 if Black)

    It is only recommended for adults >18 years. If the result exceeds 60
    ml/min/1.73m², the actual value is of little significance. Thus, it would be
    sufficient to use ">60 ml/min/1.73m²" as the result. The MDRD formula offers the
    highest accuracy in the range of 15-55 ml/min/1.73m².

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (int): Age in years
        gender (str): Gender (MALE or FEMALE)
        race (str): Race ("african_american" or "other")

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    assert creatinine > 0, "Creatinine must be positive"
    assert age > 0, "Age must be positive"
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be Gender.MALE or Gender.FEMALE")

    # Base MDRD formula: 175 x (creatinine)^-1.154 x (age)^-0.203
    egfr = 175 * (creatinine**-1.154) * (age**-0.203)

    # Apply sex correction factor
    if gender == Gender.FEMALE:
        egfr *= 0.742

    # Apply race correction factor
    if race == EthnicalRace.AFRICAN_AMERICAN:
        egfr *= 1.212

    return egfr


def ckd_epi(creatinine: float, age: int, gender: Gender, cystatin_c: float | None = None) -> float:
    """
    Calculate eGFR using 2021 CKD-EPI equation (Chronic Kidney Disease Epidemiology Collaboration)
    formula, which does not use a "race" as parameter.

    Sources:
        https://www.kidney.org/ckd-epi-creatinine-equation-2021
        https://www.kidney.org/ckd-epi-creatinine-cystatin-equation-2021

    For the same creatinine value, the 2021 equation will estimate a slightly-too-low
    GFR for Black patients and a slightly-too-high GFR for non-Black patients.

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (int): Age in years
        gender (Gender): Gender (Gender.MALE or Gender.FEMALE)
        cystain_c (optional): Cystatin c (mg/dl) - if given, it will be considered for
                the calculation

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    assert creatinine > 0, "Creatinine must be positive"
    assert age > 0, "Age must be positive"
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be of type 'Gender'")
    if cystatin_c is not None:
        assert cystatin_c > 0, "Cystatin C must be positive, if given"

    if cystatin_c is None:
        # Formula WITHOUT Cystatin C

        # Define kappa and alpha based on gender
        if gender == Gender.FEMALE:
            kappa = 0.7
            alpha = -0.241
            gender_factor = 1.012
        else:
            kappa = 0.9
            alpha = -0.302
            gender_factor = 1.0

        # Calculate min and max terms
        cr_kappa_ratio = creatinine / kappa

        # Base CKD-EPI formula
        return 142 * min(cr_kappa_ratio, 1.0) ** alpha * max(cr_kappa_ratio, 1.0) ** -1.2 * (0.9938**age) * gender_factor
    else:
        # Formula WITH Cystatin C
        # Define kappa and alpha based on gender
        if gender == Gender.FEMALE:
            kappa = 0.7
            alpha = -0.219
            gender_factor = 0.963
        else:
            kappa = 0.9
            alpha = -0.144
            gender_factor = 1.0

        cr_kappa_ratio = creatinine / kappa

        return (
            135
            * min(cr_kappa_ratio, 1.0) ** alpha
            * max(cr_kappa_ratio, 1.0) ** -0.544
            * min(cystatin_c / 0.8, 1.0) ** -0.323
            * max(cystatin_c / 0.8, 1.0) ** -0.778
            * (0.9961**age)
            * gender_factor
        )


gfr_category_titles = {
    "G1": _("Normal"),
    "G2": _("Mildly decreased"),
    "G3d": _("Mildly to moderately decreased"),
    "G3b": _("Moderately to severely decreased"),
    "G4": _("Severely decreased"),
    "G5": _("Kidney failure"),
}

ckd_progression_matrix = {
    # This represents the risk progression and suggested checks per year depending on
    # GFR category and ACR.
    "G1": (1, 1, 2),
    "G2": (1, 1, 2),
    "G3a": (1, 2, 3),
    "G3b": (2, 3, 3),
    "G4": (3, 4, 4),
    "G5": (4, 4, 4),
}


def ckd_stage(gfr: float, acr: float) -> tuple[str, str, int]:
    """
    Determine CKD stage based on GFR and ACR.

    Args:
        gfr (float): Estimated GFR in ml/min/1.73m²
        acr (float): Albumin-Creatinine-Ratio
    Returns:
        tuple[str, str, int]: Tuple with three parts:
            * CKD stage (G1-G5)
            * albumin category (A1-A3)
            * risk of progression (1-4) = recommended checks per year. If this value
                    is 4, it is recommended to make *at least* 4 checks per year.
    """
    alb_cat = 0

    if acr < 30:
        alb_cat = 1
    elif 30 < acr <= 300:
        alb_cat = 2
    elif acr > 300:
        alb_cat = 3

    if gfr >= 90:
        gfr_category = "G1"
    elif 60 <= gfr < 90:
        gfr_category = "G2"
    elif 45 <= gfr < 60:
        gfr_category = "G3a"
    elif 30 <= gfr < 45:
        gfr_category = "G3b"
    elif 15 <= gfr < 30:
        gfr_category = "G4"
    elif gfr < 15:
        gfr_category = "G5"
    else:
        raise ValueError("Unknown GFR value: {gfr}")

    #  e.g. ("G3a", "A2")
    return (
        gfr_category,
        f"A{alb_cat}",
        ckd_progression_matrix[gfr_category][alb_cat - 1],
    )
