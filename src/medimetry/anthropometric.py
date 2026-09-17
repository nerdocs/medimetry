import math
from enum import Enum
from gettext import gettext as _


class BMICategory(Enum):
    """BMI classification categories according to WHO standards."""

    UNDERWEIGHT = "underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    OBESE_CLASS_I = "obese_class_i"
    OBESE_CLASS_II = "obese_class_ii"
    OBESE_CLASS_III = "obese_class_iii"


bmi_category_titles = {
    BMICategory.UNDERWEIGHT: _("Underweight"),
    BMICategory.NORMAL: _("Normal weight"),
    BMICategory.OVERWEIGHT: _("Overweight"),
    BMICategory.OBESE_CLASS_I: _("Obese Class I"),
    BMICategory.OBESE_CLASS_II: _("Obese Class II"),
    BMICategory.OBESE_CLASS_III: _("Obese Class III"),
}


class BSAFormula(Enum):
    """Body Surface Area calculation formulas."""

    DUBOIS = "DuBois"
    MOSTELLER = "Mosteller"
    HAYCOCK = "Haycock"
    GEHAN_GEORGE = "Gehan-George"
    BOYD = "Boyd"


def bmi(weight: float, height: float) -> float:
    """
    Calculate Body Mass Index (BMI).

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters

    Returns:
        float: BMI value rounded to 1 decimal place

    Raises:
        ValueError: If weight or height are not positive or plausible
    """
    if weight <= 0:
        raise ValueError("Weight must be positive")
    if weight > 300:
        raise ValueError("Weight must be lower than 300 kilograms")
    if height <= 0:
        raise ValueError("Height must be positive")
    if height > 3:
        raise ValueError("Height must be lower than 3 meters (did you provide centimeters?)")
    bmi_value = weight / (height**2)
    return round(bmi_value, 1)


def bmi_from_cm(weight: float, height_cm: float) -> float:
    """
    Calculate BMI with height in centimeters.

    Args:
        weight (float): Weight in kilograms
        height_cm (float): Height in centimeters

    Returns:
        float: BMI value rounded to 1 decimal place

    Raises:
        ValueError: If weight or height are not positive or plausible
    """
    if height_cm <= 0:
        raise ValueError("Height must be positive")
    if height_cm <= 10:
        raise ValueError("Height must be above 10 centimeters (did you provide meters?)")

    height_m = height_cm / 100
    return bmi(weight, height_m)


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
        raise ValueError("BMI must be positive")

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


def bmi_with_category(weight: float, height: float) -> tuple[float, BMICategory]:
    """
    Calculate BMI and return with classification category.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters

    Returns:
        tuple[float, BMICategory]: BMI value and classification category
    """
    bmi_value = bmi(weight, height)
    category = bmi_category(bmi_value)
    return bmi_value, category


def bmi_with_category_cm(weight: float, height_cm: float) -> tuple[float, BMICategory]:
    """
    Calculate BMI with height in centimeters and return with classification.

    Args:
        weight (float): Weight in kilograms
        height_cm (float): Height in centimeters

    Returns:
        tuple[float, BMICategory]: BMI value and classification category
    """
    bmi_value = bmi_from_cm(weight, height_cm)
    category = bmi_category(bmi_value)
    return bmi_value, category


def bsa_dubois(weight: float, height: float) -> float:
    """
    Calculate BSA using DuBois formula.
    BSA = 0.007184 x weight^0.425 x height_cm^0.725

    References:
        Du Bois D, Du Bois EF. A formula to estimate the approximate surface area if height
        and weight be known. Arch Intern Med. 1916;17:863-871.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters

    Returns:
        float: BSA in square meters, rounded to 2 decimal places
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive")

    bsa_value = 0.007184 * (weight**0.425) * ((height * 100) ** 0.725)
    return round(bsa_value, 2)


def bsa_mosteller(weight: float, height: float) -> float:
    """
    Calculate BSA using Mosteller formula.
    BSA = sqrt((weight x height_cm) / 3600)

    References:
        Mosteller RD. Simplified calculation of body-surface area. N Engl J Med.
        1987;317(17):1098. doi:10.1056/NEJM198710223171717

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters

    Returns:
        float: BSA in square meters, rounded to 2 decimal places
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive")

    height_cm = height * 100
    bsa_value = math.sqrt((weight * height_cm) / 3600)
    return round(bsa_value, 2)


def bsa_haycock(weight: float, height: float) -> float:
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

    Returns:
        float: BSA in square meters, rounded to 2 decimal places
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive")

    height_cm = height * 100
    bsa_value = 0.024265 * (weight**0.5378) * (height_cm**0.3964)
    return round(bsa_value, 2)


def bsa_gehan_george(weight: float, height: float) -> float:
    """
    Calculate BSA using Gehan-George formula.
    BSA = 0.0235 x weight^0.51456 x height_cm^0.42246

    References:
        Gehan EA, George SL. Estimation of human body surface area from height and weight.
        Cancer Chemother Rep. 1970;54(4):225-235.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters

    Returns:
        float: BSA in square meters, rounded to 2 decimal places
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive")

    height_cm = height * 100
    bsa_value = 0.0235 * (weight**0.51456) * (height_cm**0.42246)
    return round(bsa_value, 2)


def bsa_boyd(weight: float, height: float) -> float:
    """
    Calculate BSA using Boyd formula (weight in kg form).
    BSA = 0.03330 x weight^(0.6157 - 0.0188 x log10(weight)) x height_cm^0.3

    References:
        Boyd E. The Growth of the Surface Area of the Human Body. Minneapolis:
        University of Minnesota Press; 1935.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters

    Returns:
        float: BSA in square meters, rounded to 2 decimal places
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive")

    height_cm = height * 100
    weight_exp = 0.6157 - 0.0188 * math.log10(weight)
    bsa_value = 0.03330 * (weight**weight_exp) * (height_cm**0.3)
    return round(bsa_value, 2)


def bsa(weight: float, height: float, formula: BSAFormula = BSAFormula.MOSTELLER) -> float:
    """
    Calculate Body Surface Area using specified formula.

    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
        formula (BSAFormula): Formula to use (default: Mosteller)

    Returns:
        float: BSA in square meters, rounded to 2 decimal places

    Raises:
        ValueError: If weight or height are not positive
    """
    if formula == BSAFormula.DUBOIS:
        return bsa_dubois(weight, height)
    elif formula == BSAFormula.MOSTELLER:
        return bsa_mosteller(weight, height)
    elif formula == BSAFormula.HAYCOCK:
        return bsa_haycock(weight, height)
    elif formula == BSAFormula.GEHAN_GEORGE:
        return bsa_gehan_george(weight, height)
    elif formula == BSAFormula.BOYD:
        return bsa_boyd(weight, height)
    else:
        raise ValueError(f"Unknown BSA formula: {formula}")


def bsa_from_cm(weight: float, height_cm: float, formula: BSAFormula = BSAFormula.MOSTELLER) -> float:
    """
    Calculate BSA with height in centimeters.

    Args:
        weight (float): Weight in kilograms
        height_cm (float): Height in centimeters
        formula (BSAFormula): Formula to use (default: Mosteller)

    Returns:
        float: BSA in square meters, rounded to 2 decimal places
    """
    if height_cm <= 0:
        raise ValueError("Height must be positive")

    height_m = height_cm / 100
    return bsa(weight, height_m, formula)


def bsa_all_formulas(weight: float, height: float) -> dict[str, float]:
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
        results[formula.value] = bsa(weight, height, formula)
    return results
