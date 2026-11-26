import math
from enum import Enum

from medimetry._formula import FormulaInfo
from medimetry._formula import half_up


class BMICategory(Enum):
    """BMI classification categories according to WHO standards."""

    UNDERWEIGHT = "underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    OBESE_CLASS_I = "obese_class_i"
    OBESE_CLASS_II = "obese_class_ii"
    OBESE_CLASS_III = "obese_class_iii"


class BSAFormula(Enum):
    """Body Surface Area calculation formulas."""

    DUBOIS = "DuBois"
    MOSTELLER = "Mosteller"
    HAYCOCK = "Haycock"
    GEHAN_GEORGE = "Gehan-George"
    BOYD = "Boyd"


def bmi(weight: float, height: float, *, rounded: bool = False) -> float:
    """
    Calculate Body Mass Index (BMI): weight / height².

    References:
        WHO. Obesity: preventing and managing the global epidemic. WHO Technical Report
        Series 894. Geneva: World Health Organization; 2000.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        rounded (bool): Round to ``BMI.digits`` places (half up)

    Returns:
        float: BMI in kg/m²

    >>> bmi(70, 1.75, rounded=True)
    22.9

    Raises:
        ValueError: If weight or height are not positive or plausible
    """
    if weight <= 0:
        raise ValueError(f"Weight must be positive: {weight}")
    if weight > 300:
        raise ValueError(f"Weight must be lower than 300 kilograms: {weight}")
    if height <= 0:
        raise ValueError(f"Height must be positive: {height}")
    if height > 3:
        raise ValueError(f"Height must be lower than 3 meters (did you provide centimeters?): {height}")
    bmi_value = weight / (height**2)
    return half_up(bmi_value, BMI.digits) if rounded else bmi_value


BMI = FormulaInfo(
    id="bmi",
    name="Body mass index",
    function=bmi,
    unit="kg/m2",
    inputs={"weight": "kg", "height": "m"},
    digits=1,
    citation="WHO. Obesity: preventing and managing the global epidemic. WHO TRS 894. Geneva: WHO; 2000",
    loinc="39156-5",
)


def bmi_from_cm(weight: float, height_cm: float, *, rounded: bool = False) -> float:
    """
    Calculate BMI with height in centimeters.

    Args:
        weight (float): Weight in kilograms
        height_cm (float): Height in centimeters
        rounded (bool): Round to ``BMI.digits`` places (half up)

    Returns:
        float: BMI in kg/m²

    Raises:
        ValueError: If weight or height are not positive or plausible
    """
    if height_cm <= 0:
        raise ValueError(f"Height must be positive: {height_cm}")
    if height_cm <= 10:
        raise ValueError(f"Height must be above 10 centimeters (did you provide meters?): {height_cm}")

    height_m = height_cm / 100
    return bmi(weight, height_m, rounded=rounded)


def bmi_category(bmi_value: float) -> BMICategory:
    """
    Classify BMI value into WHO categories.

    References:
        WHO. Obesity: preventing and managing the global epidemic. WHO Technical Report
        Series 894. Geneva: World Health Organization; 2000.

    Args:
        bmi_value (float): BMI value

    Returns:
        BMICategory: BMI classification category

    Raises:
        ValueError: If BMI value is not positive
    """
    if bmi_value <= 0:
        raise ValueError(f"BMI must be positive: {bmi_value}")

    if bmi_value < 18.5:
        return BMICategory.UNDERWEIGHT
    elif bmi_value < 25.0:
        return BMICategory.NORMAL
    elif bmi_value < 30.0:
        return BMICategory.OVERWEIGHT
    elif bmi_value < 35.0:
        return BMICategory.OBESE_CLASS_I
    elif bmi_value < 40.0:
        return BMICategory.OBESE_CLASS_II
    else:
        return BMICategory.OBESE_CLASS_III


def bsa_dubois(weight: float, height: float, *, rounded: bool = False) -> float:
    """
    Calculate BSA using DuBois formula.
    BSA = 0.007184 x weight^0.425 x height_cm^0.725

    References:
        Du Bois D, Du Bois EF. A formula to estimate the approximate surface area if height
        and weight be known. Arch Intern Med. 1916;17:863-871.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        rounded (bool): Round to ``BSA_DUBOIS.digits`` places (half up)

    Returns:
        float: BSA in square meters
    """
    if weight <= 0 or height <= 0:
        raise ValueError(f"Weight and height must be positive: weight={weight}, height={height}")

    bsa_value = 0.007184 * (weight**0.425) * ((height * 100) ** 0.725)
    return half_up(bsa_value, BSA_DUBOIS.digits) if rounded else bsa_value


BSA_DUBOIS = FormulaInfo(
    id="bsa_dubois",
    name="BSA (DuBois)",
    function=bsa_dubois,
    unit="m2",
    inputs={"weight": "kg", "height": "m"},
    digits=2,
    citation="Du Bois D, Du Bois EF. Arch Intern Med. 1916;17:863-871",
    loinc="8277-6",
)


def bsa_mosteller(weight: float, height: float, *, rounded: bool = False) -> float:
    """
    Calculate BSA using Mosteller formula.
    BSA = sqrt((weight x height_cm) / 3600)

    References:
        Mosteller RD. Simplified calculation of body-surface area. N Engl J Med.
        1987;317(17):1098. doi:10.1056/NEJM198710223171717

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        rounded (bool): Round to ``BSA_MOSTELLER.digits`` places (half up)

    Returns:
        float: BSA in square meters
    """
    if weight <= 0 or height <= 0:
        raise ValueError(f"Weight and height must be positive: weight={weight}, height={height}")

    height_cm = height * 100
    bsa_value = math.sqrt((weight * height_cm) / 3600)
    return half_up(bsa_value, BSA_MOSTELLER.digits) if rounded else bsa_value


BSA_MOSTELLER = FormulaInfo(
    id="bsa_mosteller",
    name="BSA (Mosteller)",
    function=bsa_mosteller,
    unit="m2",
    inputs={"weight": "kg", "height": "m"},
    digits=2,
    citation="Mosteller RD. N Engl J Med. 1987;317(17):1098. doi:10.1056/NEJM198710223171717",
    loinc="8277-6",
)


def bsa_haycock(weight: float, height: float, *, rounded: bool = False) -> float:
    """
    Calculate BSA using Haycock formula.
    BSA = 0.024265 x weight^0.5378 x height_cm^0.3964

    References:
        Haycock GB, Schwartz GJ, Wisotsky DH. Geometric method for measuring body surface
        area: a height-weight formula validated in infants, children, and adults.
        J Pediatr. 1978;93(1):62-66. doi:10.1016/s0022-3476(78)80601-5

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        rounded (bool): Round to ``BSA_HAYCOCK.digits`` places (half up)

    Returns:
        float: BSA in square meters
    """
    if weight <= 0 or height <= 0:
        raise ValueError(f"Weight and height must be positive: weight={weight}, height={height}")

    height_cm = height * 100
    bsa_value = 0.024265 * (weight**0.5378) * (height_cm**0.3964)
    return half_up(bsa_value, BSA_HAYCOCK.digits) if rounded else bsa_value


BSA_HAYCOCK = FormulaInfo(
    id="bsa_haycock",
    name="BSA (Haycock)",
    function=bsa_haycock,
    unit="m2",
    inputs={"weight": "kg", "height": "m"},
    digits=2,
    citation="Haycock GB, et al. J Pediatr. 1978;93(1):62-66. doi:10.1016/s0022-3476(78)80601-5",
    loinc="8277-6",
)


def bsa_gehan_george(weight: float, height: float, *, rounded: bool = False) -> float:
    """
    Calculate BSA using Gehan-George formula.
    BSA = 0.0235 x weight^0.51456 x height_cm^0.42246

    References:
        Gehan EA, George SL. Estimation of human body surface area from height and weight.
        Cancer Chemother Rep. 1970;54(4):225-235.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        rounded (bool): Round to ``BSA_GEHAN_GEORGE.digits`` places (half up)

    Returns:
        float: BSA in square meters
    """
    if weight <= 0 or height <= 0:
        raise ValueError(f"Weight and height must be positive: weight={weight}, height={height}")

    height_cm = height * 100
    bsa_value = 0.0235 * (weight**0.51456) * (height_cm**0.42246)
    return half_up(bsa_value, BSA_GEHAN_GEORGE.digits) if rounded else bsa_value


BSA_GEHAN_GEORGE = FormulaInfo(
    id="bsa_gehan_george",
    name="BSA (Gehan-George)",
    function=bsa_gehan_george,
    unit="m2",
    inputs={"weight": "kg", "height": "m"},
    digits=2,
    citation="Gehan EA, George SL. Cancer Chemother Rep. 1970;54(4):225-235",
    loinc="8277-6",
)


def bsa_boyd(weight: float, height: float, *, rounded: bool = False) -> float:
    """
    Calculate BSA using Boyd formula (weight in kg form).
    BSA = 0.03330 x weight^(0.6157 - 0.0188 x log10(weight)) x height_cm^0.3

    References:
        Boyd E. The Growth of the Surface Area of the Human Body. Minneapolis:
        University of Minnesota Press; 1935.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        rounded (bool): Round to ``BSA_BOYD.digits`` places (half up)

    Returns:
        float: BSA in square meters
    """
    if weight <= 0 or height <= 0:
        raise ValueError(f"Weight and height must be positive: weight={weight}, height={height}")

    height_cm = height * 100
    weight_exp = 0.6157 - 0.0188 * math.log10(weight)
    bsa_value = 0.03330 * (weight**weight_exp) * (height_cm**0.3)
    return half_up(bsa_value, BSA_BOYD.digits) if rounded else bsa_value


BSA_BOYD = FormulaInfo(
    id="bsa_boyd",
    name="BSA (Boyd)",
    function=bsa_boyd,
    unit="m2",
    inputs={"weight": "kg", "height": "m"},
    digits=2,
    citation="Boyd E. The Growth of the Surface Area of the Human Body. University of Minnesota Press; 1935",
    loinc="8277-6",
)


def bsa(weight: float, height: float, formula: BSAFormula = BSAFormula.MOSTELLER, *, rounded: bool = False) -> float:
    """
    Calculate Body Surface Area using specified formula.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        formula (BSAFormula): Formula to use (default: Mosteller)
        rounded (bool): Round to the formula's ``digits`` places (half up)

    Returns:
        float: BSA in square meters

    Raises:
        ValueError: If weight or height are not positive
    """
    if formula == BSAFormula.DUBOIS:
        return bsa_dubois(weight, height, rounded=rounded)
    elif formula == BSAFormula.MOSTELLER:
        return bsa_mosteller(weight, height, rounded=rounded)
    elif formula == BSAFormula.HAYCOCK:
        return bsa_haycock(weight, height, rounded=rounded)
    elif formula == BSAFormula.GEHAN_GEORGE:
        return bsa_gehan_george(weight, height, rounded=rounded)
    elif formula == BSAFormula.BOYD:
        return bsa_boyd(weight, height, rounded=rounded)
    else:
        raise ValueError(f"Unknown BSA formula: {formula}")


def bsa_from_cm(weight: float, height_cm: float, formula: BSAFormula = BSAFormula.MOSTELLER, *, rounded: bool = False) -> float:
    """
    Calculate BSA with height in centimeters.

    Args:
        weight (float): Weight in kilograms
        height_cm (float): Height in centimeters
        formula (BSAFormula): Formula to use (default: Mosteller)
        rounded (bool): Round to the formula's ``digits`` places (half up)

    Returns:
        float: BSA in square meters
    """
    if height_cm <= 0:
        raise ValueError(f"Height must be positive: {height_cm}")

    height_m = height_cm / 100
    return bsa(weight, height_m, formula, rounded=rounded)


def bsa_all_formulas(weight: float, height: float, *, rounded: bool = False) -> dict[str, float]:
    """
    Calculate BSA using all available formulas.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters

    Returns:
        dict[str, float]: Dictionary with formula names as keys and BSA values
    """
    results = {}
    for formula in BSAFormula:
        results[formula.value] = bsa(weight, height, formula, rounded=rounded)
    return results
