import math
from gettext import gettext as _

from medimetry.constants import EthnicalRace
from medimetry.constants import Gender


def acr(urine_albumin: float, urine_creatinine: float) -> float:
    """
    Calculate the urine Albumin-to-Creatinine Ratio (ACR) in mg/g.

    Both inputs are measured in the same (spot) urine sample. The result is expressed
    in mg albumin per g creatinine, the unit used by the KDIGO albuminuria categories
    (A1 < 30, A2 30-300, A3 > 300 mg/g).

    References:
        KDIGO 2012 Clinical Practice Guideline for the Evaluation and Management of CKD.
        Kidney Int Suppl. 2013;3(1):1-150. doi:10.1038/kisup.2012.73

    Args:
        urine_albumin (float): Urine albumin concentration in mg/dl
        urine_creatinine (float): Urine creatinine concentration in mg/dl

    Returns:
        float: Albumin-to-Creatinine Ratio in mg/g

    >>> acr(30, 100)
    300.0
    """
    assert urine_albumin >= 0, "Urine albumin must not be negative"
    assert urine_creatinine > 0, "Urine creatinine must be positive"

    return urine_albumin / urine_creatinine * 1000


def cockcroft_gault(
    age: int,
    weight: float,
    creatinine: float,
    gender: Gender,
) -> float:
    """
    Calculate creatinine clearance using Cockcroft-Gault formula.

    Note: This formula has been superseded by the CKD-EPI equation for accuracy.
    It is still occasionally used, but it is no longer recommended in the
    literature. Its disadvantages include the fact that it was derived from an
    evaluation of only 249 participants, requires laboratories to know the patient's
    body weight, and does not normalize the result to body surface area.

    References:
        Cockcroft DW, Gault MH. Prediction of creatinine clearance from serum creatinine.
        Nephron. 1976;16(1):31-41. doi:10.1159/000180580

    Args:
        age (int): Age in years
        weight (float): Weight in kg
        creatinine (float): Serum creatinine in mg/dl
        gender (Gender): Gender.MALE or Gender.FEMALE

    Returns:
        float: Creatinine clearance in mL/min, rounded to 1 decimal place
    """
    assert weight > 0, "Weight must be positive"
    assert age > 0, "Age must be positive"
    assert creatinine >= 0, "Creatinine must not be negative"
    assert gender in (Gender.MALE, Gender.FEMALE), "Gender must be Gender.MALE or Gender.FEMALE"

    if weight > 300:
        raise ValueError("Weight must be lower than 300 kilograms")
    if float(creatinine) == 0.0:
        raise ValueError("Creatinine must be non-zero")
    # Base calculation: ((140 - age) * weight) / (72 * creatinine)
    clearance = ((140 - age) * weight) / (72 * creatinine)

    # Apply sex correction factor
    if gender == Gender.FEMALE:
        clearance *= 0.85

    return round(clearance, 1)


def mdrd(creatinine: float, age: int, gender: Gender, race: EthnicalRace = EthnicalRace.OTHER) -> float:
    """
    Calculate eGFR using MDRD (Modification of Diet in Renal Disease) formula.

    Note: This formula has been superseded by the CKD-EPI equation for accuracy.

    eGFR=175 x (creatinine)^-1.154 x (age)^-0.203 x (0.742 if female) x (1.212 if Black)

    References:
        Levey AS, et al. Using standardized serum creatinine values in the modification of
        diet in renal disease study equation for estimating glomerular filtration rate.
        Ann Intern Med. 2006;145(4):247-254. doi:10.7326/0003-4819-145-4-200608150-00004

    It is only recommended for adults >18 years. If the result exceeds 60
    ml/min/1.73m², the actual value is of little significance. Thus, it would be
    sufficient to use ">60 ml/min/1.73m²" as the result. The MDRD formula offers the
    highest accuracy in the range of 15-55 ml/min/1.73m².

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (int): Age in years
        gender (Gender): Gender.MALE or Gender.FEMALE
        race (EthnicalRace): EthnicalRace.AFRICAN_AMERICAN applies the 1.212 factor, any other value does not

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    assert creatinine > 0, "Creatinine must be positive"
    assert age > 0, "Age must be positive"
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be Gender.MALE or Gender.FEMALE")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")

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

    References:
        Inker LA, et al. New Creatinine- and Cystatin C-Based Equations to Estimate GFR without Race.
        N Engl J Med. 2021;385(19):1737-1749. doi:10.1056/NEJMoa2102953
        https://www.kidney.org/ckd-epi-creatinine-equation-2021
        https://www.kidney.org/ckd-epi-creatinine-cystatin-equation-2021

    For the same creatinine value, the 2021 equation will estimate a slightly-too-low
    GFR for Black patients and a slightly-too-high GFR for non-Black patients.

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (int): Age in years
        gender (Gender): Gender (Gender.MALE or Gender.FEMALE)
        cystatin_c (float, optional): Serum cystatin C in mg/L - if given, the
                creatinine-cystatin C equation is used

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    assert creatinine > 0, "Creatinine must be positive"
    assert age > 0, "Age must be positive"
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be of type 'Gender'")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")
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


def _ekfc(ratio: float, age: float) -> float:
    """EKFC core: 107.3 x (biomarker/Q)^alpha x 0.990^(age-40) above 40 years."""
    egfr = 107.3 * ratio ** (-0.322 if ratio < 1 else -1.132)
    if age > 40:
        egfr *= 0.990 ** (age - 40)
    return egfr


def ekfc(creatinine: float, age: float, gender: Gender, cystatin_c: float | None = None) -> float:
    """
    Calculate eGFR using the EKFC (European Kidney Function Consortium) equation.

    The equation covers the full age spectrum (from 2 years on) with one formula: serum
    creatinine is rescaled by Q, the median creatinine of healthy persons of the same age
    and sex. Q is a polynomial in age for 2-25 years, and 80 µmol/l (men) or 62 µmol/l
    (women) above 25 years. The creatinine is converted to µmol/l internally, as Q is
    published in µmol/l.

    If cystatin C is given, the result is the arithmetic mean of the creatinine-based and
    the cystatin C-based EKFC equation, as proposed by Pottel et al. (2023). The cystatin C
    equation uses Q = 0.83 mg/l below 50 years and 0.83 + 0.005 x (age - 50) mg/l above,
    regardless of sex. The same Q of 0.83 mg/l is used for children (Pottel et al., 2024).

    The equation was developed in white European populations and is not validated for
    Black patients.

    References:
        Pottel H, et al. Development and Validation of a Modified Full Age Spectrum
        Creatinine-Based Equation to Estimate Glomerular Filtration Rate.
        Ann Intern Med. 2021;174(2):183-191. doi:10.7326/M20-4366

        Pottel H, et al. Cystatin C-Based Equation to Estimate GFR without the Inclusion of
        Race and Sex. N Engl J Med. 2023;388(4):333-343. doi:10.1056/NEJMoa2203769

        Pottel H, et al. Extending the cystatin C based EKFC-equation to children - validation
        results from Europe. Pediatr Nephrol. 2024;39(4):1177-1183. doi:10.1007/s00467-023-06192-6

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (float): Age in years (fractions are significant for children)
        gender (Gender): Gender.MALE or Gender.FEMALE
        cystatin_c (float, optional): Serum cystatin C in mg/l - if given, the mean of the
                creatinine and the cystatin C equation is returned

    Returns:
        float: Estimated GFR in mL/min/1.73m²

    >>> round(ekfc(creatinine=1.0, age=50, gender=Gender.MALE), 1)
    86.7
    """
    assert creatinine > 0, "Creatinine must be positive"
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be of type 'Gender'")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")
    if cystatin_c is not None:
        assert cystatin_c > 0, "Cystatin C must be positive, if given"
    if age < 2:
        raise ValueError(f"EKFC is only defined from 2 years of age: {age}")

    if age <= 25:
        if gender == Gender.FEMALE:
            q = math.exp(3.080 + 0.177 * age - 0.223 * math.log(age) - 0.00596 * age**2 + 0.0000686 * age**3)
        else:
            q = math.exp(3.200 + 0.259 * age - 0.543 * math.log(age) - 0.00763 * age**2 + 0.0000790 * age**3)
    else:
        q = 62.0 if gender == Gender.FEMALE else 80.0

    # Q is published in µmol/l
    egfr_cr = _ekfc(creatinine * 88.4 / q, age)
    if cystatin_c is None:
        return egfr_cr

    q_cys = 0.83 if age < 50 else 0.83 + 0.005 * (age - 50)
    return (egfr_cr + _ekfc(cystatin_c / q_cys, age)) / 2


gfr_category_titles = {
    "G1": _("Normal"),
    "G2": _("Mildly decreased"),
    "G3a": _("Mildly to moderately decreased"),
    "G3b": _("Moderately to severely decreased"),
    "G4": _("Severely decreased"),
    "G5": _("Kidney failure"),
}

kdigo_risk_matrix = {
    # KDIGO prognosis-of-CKD heat map: risk category (1 = low/green, 2 = moderately
    # increased/yellow, 3 = high/orange, 4 = very high/red) per GFR category (row)
    # and albuminuria category A1, A2, A3 (columns).
    "G1": (1, 2, 3),
    "G2": (1, 2, 3),
    "G3a": (2, 3, 4),
    "G3b": (3, 4, 4),
    "G4": (4, 4, 4),
    "G5": (4, 4, 4),
}


def ckd_stage(gfr: float, acr: float) -> tuple[str, str, int]:
    """
    Determine KDIGO CKD categories based on GFR and ACR.

    References:
        KDIGO 2012 Clinical Practice Guideline for the Evaluation and Management of CKD.
        Kidney Int Suppl. 2013;3(1):1-150. doi:10.1038/kisup.2012.73 (Figure 5)

    Args:
        gfr (float): Estimated GFR in ml/min/1.73m²
        acr (float): Urine Albumin-Creatinine-Ratio in mg/g
    Returns:
        tuple[str, str, int]: Tuple with three parts:
            * GFR category (G1, G2, G3a, G3b, G4, G5)
            * albuminuria category (A1-A3)
            * KDIGO prognosis risk category (1 = low, 2 = moderately increased,
              3 = high, 4 = very high) as published in the KDIGO heat map

    >>> ckd_stage(50, 400)
    ('G3a', 'A3', 4)
    """
    if acr < 0:
        raise ValueError(f"ACR must not be negative: {acr}")

    if acr < 30:
        alb_cat = 1
    elif 30 <= acr <= 300:
        alb_cat = 2
    elif acr > 300:
        alb_cat = 3
    else:
        raise ValueError(f"Unknown ACR value: {acr}")

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
    elif 0 < gfr < 15:
        gfr_category = "G5"
    else:
        raise ValueError(f"Invalid GFR value: {gfr}")

    #  e.g. ("G3a", "A2")
    return (
        gfr_category,
        f"A{alb_cat}",
        kdigo_risk_matrix[gfr_category][alb_cat - 1],
    )
