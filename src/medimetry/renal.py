import math

from medimetry._formula import FormulaInfo
from medimetry._formula import check_age
from medimetry._formula import half_up
from medimetry.constants import EthnicalRace
from medimetry.constants import Gender
from medimetry.constants import KfreRegion


def acr(urine_albumin: float, urine_creatinine: float, *, rounded: bool = False) -> float:
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
        rounded (bool): Round to ``ACR.digits`` places (half up)

    Returns:
        float: Albumin-to-Creatinine Ratio in mg/g

    >>> acr(30, 100)
    300.0
    """
    if not (urine_albumin >= 0):
        raise ValueError("Urine albumin must not be negative")
    if not (urine_creatinine > 0):
        raise ValueError("Urine creatinine must be positive")

    value = urine_albumin / urine_creatinine * 1000
    return half_up(value, ACR.digits) if rounded else value


ACR = FormulaInfo(
    id="acr",
    name="Albumin/creatinine ratio",
    function=acr,
    unit="mg/g",
    inputs={"urine_albumin": "mg/dL", "urine_creatinine": "mg/dL"},
    digits=1,
    citation="KDIGO 2012 CKD guideline. Kidney Int Suppl. 2013;3(1):1-150. doi:10.1038/kisup.2012.73",
    loinc="9318-7",
)


def cockcroft_gault(
    age: int,
    weight: float,
    creatinine: float,
    gender: Gender,
    *,
    rounded: bool = False,
) -> float:
    """
    Calculate creatinine clearance using Cockcroft-Gault formula.

    The equation was derived from 249 participants aged 18-92 years. It requires body
    weight and returns creatinine clearance in ml/min, not normalized to body surface area.

    References:
        Cockcroft DW, Gault MH. Prediction of creatinine clearance from serum creatinine.
        Nephron. 1976;16(1):31-41. doi:10.1159/000180580

    Args:
        age (int): Age in years
        weight (float): Weight in kg
        creatinine (float): Serum creatinine in mg/dl
        gender (Gender): Gender.MALE or Gender.FEMALE
        rounded (bool): Round to ``COCKCROFT_GAULT.digits`` places (half up)

    Returns:
        float: Creatinine clearance in mL/min
    """
    if not (weight > 0):
        raise ValueError("Weight must be positive")
    if not (age > 0):
        raise ValueError("Age must be positive")
    if not (creatinine >= 0):
        raise ValueError("Creatinine must not be negative")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")
    check_age(COCKCROFT_GAULT, age)

    if weight > 300:
        raise ValueError("Weight must be lower than 300 kilograms")
    if float(creatinine) == 0.0:
        raise ValueError("Creatinine must be non-zero")
    # Base calculation: ((140 - age) * weight) / (72 * creatinine)
    clearance = ((140 - age) * weight) / (72 * creatinine)

    # Apply sex correction factor
    if gender == Gender.FEMALE:
        clearance *= 0.85

    return half_up(clearance, COCKCROFT_GAULT.digits) if rounded else clearance


COCKCROFT_GAULT = FormulaInfo(
    id="cockcroft_gault",
    name="Creatinine clearance (Cockcroft-Gault)",
    function=cockcroft_gault,
    unit="mL/min",
    inputs={"weight": "kg", "creatinine": "mg/dL"},
    digits=1,
    citation="Cockcroft DW, Gault MH. Nephron. 1976;16(1):31-41. doi:10.1159/000180580",
    min_age=18,
)


def mdrd(creatinine: float, age: float, gender: Gender, race: EthnicalRace = EthnicalRace.OTHER, *, rounded: bool = False) -> float:
    """
    Calculate eGFR using MDRD (Modification of Diet in Renal Disease) formula.

    eGFR=175 x (creatinine)^-1.154 x (age)^-0.203 x (0.742 if female) x (1.212 if Black)

    References:
        Levey AS, et al. Using standardized serum creatinine values in the modification of
        diet in renal disease study equation for estimating glomerular filtration rate.
        Ann Intern Med. 2006;145(4):247-254. doi:10.7326/0003-4819-145-4-200608150-00004

    The equation was derived in adults (> 18 years) with chronic kidney disease; below 18 years it raises.

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (float): Age in years
        gender (Gender): Gender.MALE or Gender.FEMALE
        race (EthnicalRace): EthnicalRace.AFRICAN_AMERICAN applies the 1.212 factor, any other value does not
        rounded (bool): Round to ``MDRD.digits`` places (half up)

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    if not (creatinine > 0):
        raise ValueError("Creatinine must be positive")
    if not (age > 0):
        raise ValueError("Age must be positive")
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be Gender.MALE or Gender.FEMALE")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")
    check_age(MDRD, age)

    # Base MDRD formula: 175 x (creatinine)^-1.154 x (age)^-0.203
    egfr = 175 * (creatinine**-1.154) * (age**-0.203)

    # Apply sex correction factor
    if gender == Gender.FEMALE:
        egfr *= 0.742

    # Apply race correction factor
    if race == EthnicalRace.AFRICAN_AMERICAN:
        egfr *= 1.212

    return half_up(egfr, MDRD.digits) if rounded else egfr


EGFR_UNIT = "mL/min/{1.73_m2}"

MDRD = FormulaInfo(
    id="mdrd",
    name="eGFR (MDRD)",
    function=mdrd,
    unit=EGFR_UNIT,
    inputs={"creatinine": "mg/dL"},
    input_loinc={"creatinine": "2160-0"},
    digits=1,
    citation="Levey AS, et al. Ann Intern Med. 2006;145(4):247-254. doi:10.7326/0003-4819-145-4-200608150-00004",
    loinc="33914-3",
    min_age=18,
)


def _check_ckd_epi(creatinine: float, gender: Gender) -> None:
    if not (creatinine > 0):
        raise ValueError("Creatinine must be positive")
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be of type 'Gender'")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")


def ckd_epi_2021(creatinine: float, age: float, gender: Gender, *, rounded: bool = False) -> float:
    """
    Calculate eGFR using the 2021 CKD-EPI creatinine equation, which does not use race.

    eGFR = 142 x min(Scr/k, 1)^a x max(Scr/k, 1)^-1.200 x 0.9938^age x (1.012 if female)

    with k = 0.7 (female) / 0.9 (male) and a = -0.241 (female) / -0.302 (male). The equation was
    derived in adults; below 18 years it raises. With cystatin C: ``ckd_epi_2021_cystatin``.

    References:
        Inker LA, et al. New Creatinine- and Cystatin C-Based Equations to Estimate GFR without Race.
        N Engl J Med. 2021;385(19):1737-1749. doi:10.1056/NEJMoa2102953
        https://www.kidney.org/ckd-epi-creatinine-equation-2021

    For the same creatinine value, the 2021 equation will estimate a slightly-too-low
    GFR for Black patients and a slightly-too-high GFR for non-Black patients.

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (float): Age in years
        gender (Gender): Gender (Gender.MALE or Gender.FEMALE)
        rounded (bool): Round to ``CKD_EPI_2021.digits`` places (half up)

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    _check_ckd_epi(creatinine, gender)
    check_age(CKD_EPI_2021, age)

    if gender == Gender.FEMALE:
        kappa, alpha, gender_factor = 0.7, -0.241, 1.012
    else:
        kappa, alpha, gender_factor = 0.9, -0.302, 1.0

    cr_kappa_ratio = creatinine / kappa
    egfr = 142 * min(cr_kappa_ratio, 1.0) ** alpha * max(cr_kappa_ratio, 1.0) ** -1.2 * (0.9938**age) * gender_factor
    return half_up(egfr, CKD_EPI_2021.digits) if rounded else egfr


def ckd_epi_2021_cystatin(creatinine: float, cystatin_c: float, age: float, gender: Gender, *, rounded: bool = False) -> float:
    """
    Calculate eGFR using the 2021 CKD-EPI creatinine-cystatin C equation, which does not use race.

    eGFR = 135 x min(Scr/k, 1)^a x max(Scr/k, 1)^-0.544 x min(Scys/0.8, 1)^-0.323 x max(Scys/0.8, 1)^-0.778
    x 0.9961^age x (0.963 if female), with k = 0.7 (female) / 0.9 (male) and a = -0.219 (female) / -0.144 (male).
    Derived in adults; below 18 years it raises.

    References:
        Inker LA, et al. New Creatinine- and Cystatin C-Based Equations to Estimate GFR without Race.
        N Engl J Med. 2021;385(19):1737-1749. doi:10.1056/NEJMoa2102953
        https://www.kidney.org/ckd-epi-creatinine-cystatin-equation-2021

    Args:
        creatinine (float): Serum creatinine in mg/dl
        cystatin_c (float): Serum cystatin C in mg/L
        age (float): Age in years
        gender (Gender): Gender (Gender.MALE or Gender.FEMALE)
        rounded (bool): Round to ``CKD_EPI_2021_CYSTATIN.digits`` places (half up)

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    _check_ckd_epi(creatinine, gender)
    if not (cystatin_c > 0):
        raise ValueError("Cystatin C must be positive")
    check_age(CKD_EPI_2021_CYSTATIN, age)

    if gender == Gender.FEMALE:
        kappa, alpha, gender_factor = 0.7, -0.219, 0.963
    else:
        kappa, alpha, gender_factor = 0.9, -0.144, 1.0

    cr_kappa_ratio = creatinine / kappa
    egfr = (
        135
        * min(cr_kappa_ratio, 1.0) ** alpha
        * max(cr_kappa_ratio, 1.0) ** -0.544
        * min(cystatin_c / 0.8, 1.0) ** -0.323
        * max(cystatin_c / 0.8, 1.0) ** -0.778
        * (0.9961**age)
        * gender_factor
    )
    return half_up(egfr, CKD_EPI_2021_CYSTATIN.digits) if rounded else egfr


def ckd_epi(creatinine: float, age: float, gender: Gender, *, rounded: bool = False) -> float:
    """
    Calculate eGFR using the newest CKD-EPI creatinine equation — currently ``ckd_epi_2021``.

    Follows the newest equation as medimetry adds it. Store ``CKD_EPI_2021.id`` (not ``"ckd_epi"``) to record
    which equation produced a value.
    """
    return ckd_epi_2021(creatinine, age, gender, rounded=rounded)


CKD_EPI_2021 = FormulaInfo(
    id="ckd_epi_2021",
    name="eGFR (CKD-EPI 2021)",
    function=ckd_epi_2021,
    unit=EGFR_UNIT,
    inputs={"creatinine": "mg/dL"},
    input_loinc={"creatinine": "2160-0"},
    digits=1,
    citation="Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749. doi:10.1056/NEJMoa2102953",
    loinc="98979-8",
    min_age=18,
)

CKD_EPI_2021_CYSTATIN = FormulaInfo(
    id="ckd_epi_2021_cystatin",
    name="eGFR (CKD-EPI 2021, creatinine and cystatin C)",
    function=ckd_epi_2021_cystatin,
    unit=EGFR_UNIT,
    inputs={"creatinine": "mg/dL", "cystatin_c": "mg/L"},
    input_loinc={"creatinine": "2160-0", "cystatin_c": "33863-2"},
    digits=1,
    citation="Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749. doi:10.1056/NEJMoa2102953",
    min_age=18,
)


def ckd_epi_2009(creatinine: float, age: float, gender: Gender, race: EthnicalRace = EthnicalRace.OTHER, *, rounded: bool = False) -> float:
    """
    Calculate eGFR using the 2009 CKD-EPI creatinine equation.

    eGFR = 141 x min(Scr/k, 1)^a x max(Scr/k, 1)^-1.209 x 0.993^age x (1.018 if female) x (1.159 if Black)

    with k = 0.7 (female) / 0.9 (male) and a = -0.329 (female) / -0.411 (male). Superseded by the 2021
    equation (``ckd_epi_2021``), which drops the race coefficient; still reported by laboratories. Derived in
    adults; below 18 years it raises.

    References:
        Levey AS, et al. A New Equation to Estimate Glomerular Filtration Rate.
        Ann Intern Med. 2009;150(9):604-612. doi:10.7326/0003-4819-150-9-200905050-00006

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (int): Age in years
        gender (Gender): Gender.MALE or Gender.FEMALE
        race (EthnicalRace): EthnicalRace.AFRICAN_AMERICAN applies the 1.159 factor, any other value does not
        rounded (bool): Round to ``CKD_EPI_2009.digits`` places (half up)

    Returns:
        float: Estimated GFR in mL/min/1.73m²

    >>> ckd_epi_2009(creatinine=1.5, age=70, gender=Gender.MALE, rounded=True)
    46.5
    """
    _check_ckd_epi(creatinine, gender)
    check_age(CKD_EPI_2009, age)

    if gender == Gender.FEMALE:
        kappa = 0.7
        alpha = -0.329
        gender_factor = 1.018
    else:
        kappa = 0.9
        alpha = -0.411
        gender_factor = 1.0

    cr_kappa_ratio = creatinine / kappa
    egfr = 141 * min(cr_kappa_ratio, 1.0) ** alpha * max(cr_kappa_ratio, 1.0) ** -1.209 * (0.993**age) * gender_factor

    if race == EthnicalRace.AFRICAN_AMERICAN:
        egfr *= 1.159

    return half_up(egfr, CKD_EPI_2009.digits) if rounded else egfr


CKD_EPI_2009 = FormulaInfo(
    id="ckd_epi_2009",
    name="eGFR (CKD-EPI 2009)",
    function=ckd_epi_2009,
    unit=EGFR_UNIT,
    inputs={"creatinine": "mg/dL"},
    input_loinc={"creatinine": "2160-0"},
    digits=1,
    citation="Levey AS, et al. Ann Intern Med. 2009;150(9):604-612. doi:10.7326/0003-4819-150-9-200905050-00006",
    loinc="62238-1",
    min_age=18,
)


def _ekfc(ratio: float, age: float) -> float:
    """EKFC core: 107.3 x (biomarker/Q)^alpha x 0.990^(age-40) above 40 years."""
    egfr = 107.3 * ratio ** (-0.322 if ratio < 1 else -1.132)
    if age > 40:
        egfr *= 0.990 ** (age - 40)
    return egfr


def _ekfc_q(age: float, gender: Gender) -> float:
    """Q of the creatinine equation in µmol/l: a polynomial in age up to 25 years, 80 (men) / 62 (women) above."""
    if age <= 25:
        if gender == Gender.FEMALE:
            return math.exp(3.080 + 0.177 * age - 0.223 * math.log(age) - 0.00596 * age**2 + 0.0000686 * age**3)
        return math.exp(3.200 + 0.259 * age - 0.543 * math.log(age) - 0.00763 * age**2 + 0.0000790 * age**3)
    return 62.0 if gender == Gender.FEMALE else 80.0


def _check_ekfc(creatinine: float, gender: Gender, info: FormulaInfo, age: float) -> None:
    if not (creatinine > 0):
        raise ValueError("Creatinine must be positive")
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be of type 'Gender'")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")
    check_age(info, age)


def ekfc(creatinine: float, age: float, gender: Gender, *, rounded: bool = False) -> float:
    """
    Calculate eGFR using the EKFC (European Kidney Function Consortium) creatinine equation.

    The equation covers the full age spectrum (from 2 years on) with one formula: serum
    creatinine is rescaled by Q, the median creatinine of healthy persons of the same age
    and sex. Q is a polynomial in age for 2-25 years, and 80 µmol/l (men) or 62 µmol/l
    (women) above 25 years. The creatinine is converted to µmol/l internally, as Q is
    published in µmol/l. With cystatin C: ``ekfc_cystatin``.

    The equation was developed in white European populations and is not validated for
    Black patients.

    References:
        Pottel H, et al. Development and Validation of a Modified Full Age Spectrum
        Creatinine-Based Equation to Estimate Glomerular Filtration Rate.
        Ann Intern Med. 2021;174(2):183-191. doi:10.7326/M20-4366

    Args:
        creatinine (float): Serum creatinine in mg/dl
        age (float): Age in years (fractions are significant for children)
        gender (Gender): Gender.MALE or Gender.FEMALE
        rounded (bool): Round to ``EKFC.digits`` places (half up)

    Returns:
        float: Estimated GFR in mL/min/1.73m²

    >>> ekfc(creatinine=1.0, age=50, gender=Gender.MALE, rounded=True)
    86.7
    """
    _check_ekfc(creatinine, gender, EKFC, age)
    # Q is published in µmol/l
    egfr = _ekfc(creatinine * 88.4 / _ekfc_q(age, gender), age)
    return half_up(egfr, EKFC.digits) if rounded else egfr


def ekfc_cystatin(creatinine: float, cystatin_c: float, age: float, gender: Gender, *, rounded: bool = False) -> float:
    """
    Calculate eGFR as the arithmetic mean of the EKFC creatinine and the EKFC cystatin C equation.

    The mean is the combination proposed by Pottel et al. (2023). The cystatin C equation uses
    Q = 0.83 mg/l below 50 years and 0.83 + 0.005 x (age - 50) mg/l above, regardless of sex;
    the same Q of 0.83 mg/l is used for children (Pottel et al., 2024).

    References:
        Pottel H, et al. Ann Intern Med. 2021;174(2):183-191. doi:10.7326/M20-4366

        Pottel H, et al. Cystatin C-Based Equation to Estimate GFR without the Inclusion of
        Race and Sex. N Engl J Med. 2023;388(4):333-343. doi:10.1056/NEJMoa2203769

        Pottel H, et al. Extending the cystatin C based EKFC-equation to children - validation
        results from Europe. Pediatr Nephrol. 2024;39(4):1177-1183. doi:10.1007/s00467-023-06192-6

    Args:
        creatinine (float): Serum creatinine in mg/dl
        cystatin_c (float): Serum cystatin C in mg/l
        age (float): Age in years (fractions are significant for children)
        gender (Gender): Gender.MALE or Gender.FEMALE
        rounded (bool): Round to ``EKFC_CYSTATIN.digits`` places (half up)

    Returns:
        float: Estimated GFR in mL/min/1.73m²
    """
    _check_ekfc(creatinine, gender, EKFC_CYSTATIN, age)
    if not (cystatin_c > 0):
        raise ValueError("Cystatin C must be positive")
    egfr_cr = _ekfc(creatinine * 88.4 / _ekfc_q(age, gender), age)
    q_cys = 0.83 if age < 50 else 0.83 + 0.005 * (age - 50)
    egfr = (egfr_cr + _ekfc(cystatin_c / q_cys, age)) / 2
    return half_up(egfr, EKFC_CYSTATIN.digits) if rounded else egfr


EKFC = FormulaInfo(
    id="ekfc",
    name="eGFR (EKFC)",
    function=ekfc,
    unit=EGFR_UNIT,
    inputs={"creatinine": "mg/dL"},
    input_loinc={"creatinine": "2160-0"},
    digits=1,
    citation="Pottel H, et al. Ann Intern Med. 2021;174(2):183-191. doi:10.7326/M20-4366",
    min_age=2,
)

EKFC_CYSTATIN = FormulaInfo(
    id="ekfc_cystatin",
    name="eGFR (EKFC, creatinine and cystatin C)",
    function=ekfc_cystatin,
    unit=EGFR_UNIT,
    inputs={"creatinine": "mg/dL", "cystatin_c": "mg/L"},
    input_loinc={"creatinine": "2160-0", "cystatin_c": "33863-2"},
    digits=1,
    citation="Pottel H, et al. N Engl J Med. 2023;388(4):333-343. doi:10.1056/NEJMoa2203769",
    min_age=2,
)


# Baseline survival of the 4-variable KFRE per region (Tangri 2016, eAppendix 2)
_KFRE_SURVIVAL_2_YEAR = {KfreRegion.NORTH_AMERICA: 0.9750, KfreRegion.NON_NORTH_AMERICA: 0.9832}
_KFRE_SURVIVAL_5_YEAR = {KfreRegion.NORTH_AMERICA: 0.9240, KfreRegion.NON_NORTH_AMERICA: 0.9365}


def _kfre(
    egfr: float, acr: float, age: float, gender: Gender, region: KfreRegion, survival: dict[KfreRegion, float], info: FormulaInfo
) -> float:
    """4-variable KFRE in percent: 100 x (1 - S0^exp(L)), S0 the baseline survival of ``region``."""
    if not isinstance(gender, Gender):
        raise TypeError("Gender must be of type 'Gender'")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError("Gender must be Gender.MALE or Gender.FEMALE")
    if not isinstance(region, KfreRegion):
        raise TypeError("Region must be of type 'KfreRegion'")
    if not (0 < egfr < 60):
        raise ValueError(f"{info.name} is only defined for an eGFR below 60 mL/min/1.73m² (and above 0): {egfr}")
    if not (acr > 0):
        raise ValueError("ACR must be positive")
    if not (age > 0):
        raise ValueError("Age must be positive")
    check_age(info, age)

    male = 1 if gender == Gender.MALE else 0
    linear_predictor = (
        -0.2201 * (age / 10 - 7.036) + 0.2467 * (male - 0.5642) - 0.5567 * (egfr / 5 - 7.222) + 0.4510 * (math.log(acr) - 5.137)
    )
    return 100 * (1 - survival[region] ** math.exp(linear_predictor))


def kfre_2_year(egfr: float, acr: float, age: float, gender: Gender, region: KfreRegion, *, rounded: bool = False) -> float:
    """
    Calculate the 2-year risk of kidney failure using the 4-variable Kidney Failure Risk Equation (KFRE).

    risk = 1 - S0^exp(L), with

    L = -0.2201 x (age/10 - 7.036) + 0.2467 x (male - 0.5642) - 0.5567 x (eGFR/5 - 7.222) + 0.4510 x (ln(ACR) - 5.137)

    male = 1 for men and 0 for women; S0 (2 years) = 0.9750 for North America and 0.9832 for all other regions.
    These are the pooled equations of Tangri et al. (2016), which recalibrated the equation developed in two
    Canadian cohorts (Tangri et al., 2011) in 31 cohorts from 30 countries. There is no default region.

    Kidney failure is treatment by dialysis or kidney transplantation. The equations were developed and validated
    in adults with CKD stages 3-5 (eGFR < 60 mL/min/1.73m²); outside that domain the function raises. The cohorts
    estimated GFR with the CKD-EPI 2009 creatinine equation. 5-year risk: ``kfre_5_year``.

    References:
        Tangri N, et al. Multinational Assessment of Accuracy of Equations for Predicting Risk of Kidney
        Failure: A Meta-analysis. JAMA. 2016;315(2):164-174. doi:10.1001/jama.2015.18202 (eAppendix 2)

        Tangri N, et al. A predictive model for progression of chronic kidney disease to kidney failure.
        JAMA. 2011;305(15):1553-1559. doi:10.1001/jama.2011.451

    Args:
        egfr (float): Estimated GFR in mL/min/1.73m²
        acr (float): Urine albumin-to-creatinine ratio in mg/g (as returned by ``acr``)
        age (float): Age in years
        gender (Gender): Gender.MALE or Gender.FEMALE
        region (KfreRegion): KfreRegion.NORTH_AMERICA or KfreRegion.NON_NORTH_AMERICA
        rounded (bool): Round to ``KFRE_2_YEAR.digits`` places (half up)

    Returns:
        float: 2-year risk of kidney failure in percent

    >>> kfre_2_year(egfr=30, acr=300, age=65, gender=Gender.MALE, region=KfreRegion.NON_NORTH_AMERICA, rounded=True)
    5.27
    """
    risk = _kfre(egfr, acr, age, gender, region, _KFRE_SURVIVAL_2_YEAR, KFRE_2_YEAR)
    return half_up(risk, KFRE_2_YEAR.digits) if rounded else risk


def kfre_5_year(egfr: float, acr: float, age: float, gender: Gender, region: KfreRegion, *, rounded: bool = False) -> float:
    """
    Calculate the 5-year risk of kidney failure using the 4-variable Kidney Failure Risk Equation (KFRE).

    The linear predictor L, the domain and the arguments are those of ``kfre_2_year``; the baseline survival
    S0 (5 years) is 0.9240 for North America and 0.9365 for all other regions.

    References:
        Tangri N, et al. Multinational Assessment of Accuracy of Equations for Predicting Risk of Kidney
        Failure: A Meta-analysis. JAMA. 2016;315(2):164-174. doi:10.1001/jama.2015.18202 (eAppendix 2)

        Tangri N, et al. A predictive model for progression of chronic kidney disease to kidney failure.
        JAMA. 2011;305(15):1553-1559. doi:10.1001/jama.2011.451

    Args:
        egfr (float): Estimated GFR in mL/min/1.73m²
        acr (float): Urine albumin-to-creatinine ratio in mg/g (as returned by ``acr``)
        age (float): Age in years
        gender (Gender): Gender.MALE or Gender.FEMALE
        region (KfreRegion): KfreRegion.NORTH_AMERICA or KfreRegion.NON_NORTH_AMERICA
        rounded (bool): Round to ``KFRE_5_YEAR.digits`` places (half up)

    Returns:
        float: 5-year risk of kidney failure in percent

    >>> kfre_5_year(egfr=30, acr=300, age=65, gender=Gender.MALE, region=KfreRegion.NON_NORTH_AMERICA, rounded=True)
    18.91
    """
    risk = _kfre(egfr, acr, age, gender, region, _KFRE_SURVIVAL_5_YEAR, KFRE_5_YEAR)
    return half_up(risk, KFRE_5_YEAR.digits) if rounded else risk


_KFRE_CITATION = "Tangri N, et al. JAMA. 2016;315(2):164-174. doi:10.1001/jama.2015.18202"

KFRE_2_YEAR = FormulaInfo(
    id="kfre_2_year",
    name="Kidney failure 2-year risk (KFRE, 4 variables)",
    function=kfre_2_year,
    unit="%",
    inputs={"egfr": EGFR_UNIT, "acr": "mg/g"},
    input_loinc={"acr": "9318-7"},
    digits=2,
    citation=_KFRE_CITATION,
    loinc="85624-5",
    min_age=18,
)

KFRE_5_YEAR = FormulaInfo(
    id="kfre_5_year",
    name="Kidney failure 5-year risk (KFRE, 4 variables)",
    function=kfre_5_year,
    unit="%",
    inputs={"egfr": EGFR_UNIT, "acr": "mg/g"},
    input_loinc={"acr": "9318-7"},
    digits=2,
    citation=_KFRE_CITATION,
    loinc="85625-2",
    min_age=18,
)


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
