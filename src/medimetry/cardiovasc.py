from enum import Enum

from medimetry import Gender


class FraminghamRiskLevel(Enum):
    """Framingham risk level categories."""

    LOW = "Low"
    INTERMEDIATE = "Intermediate"
    HIGH = "High"


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
    gender: Gender,
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
        gender (Gender): Gender (Gender.MALE or Gender.FEMALE)
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
    assert gender in (
        Gender.MALE,
        Gender.FEMALE,
    ), "Gender must be Gender.MALE or Gender.FEMALE"

    score = 0

    # Age scoring
    if age >= 75:
        score += 2
    elif age >= 65:
        score += 1

    # Gender category - female?
    if gender == Gender.FEMALE:
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


def calcium_correction(total_calcium: float, albumin: float) -> float:
    """
    Calculate corrected calcium for hypo-/hyperalbuminemia.

    Uses the formula: Corrected Ca = Total Ca + 0.8 x (4.0 - Albumin)

    Args:
        total_calcium (float): Total serum calcium in mg/dl
        albumin (float): Serum albumin in g/dl

    Returns:
        float: Corrected calcium in mg/dl

    Raises:
        ValueError: If calcium or albumin values are negative
    """
    normal_calcium = 4.0
    if total_calcium < 0:
        raise ValueError("Total calcium must be non-negative")
    if albumin < 0:
        raise ValueError("Albumin must be non-negative")

    corrected_calcium = total_calcium + 0.8 * (normal_calcium - albumin)
    return round(corrected_calcium, 2)


def framingham_risk_score(
    age: int,
    gender: Gender,
    total_cholesterol: float,
    hdl_cholesterol: float,
    systolic_bp: int,
    bp_treatment: bool = False,
    smoking: bool = False,
    diabetes: bool = False,
) -> tuple[int, float, FraminghamRiskLevel]:
    """
    Calculate Framingham Risk Score for 10-year cardiovascular disease risk.

    Based on the ATP III guidelines for cardiovascular risk assessment.

    Args:
        age (int): Age in years (30-79)
        gender (Gender): Gender (Gender.MALE or Gender.FEMALE)
        total_cholesterol (float): Total cholesterol in mmol/l
        hdl_cholesterol (float): HDL cholesterol in mmol/l
        systolic_bp (int): Systolic blood pressure in mmHg
        bp_treatment (bool): Whether patient is on antihypertensive treatment
        smoking (bool): Current smoking status
        diabetes (bool): Presence of diabetes mellitus

    Returns:
        tuple[int, float, FraminghamRiskLevel]: Points, 10-year risk percentage, risk level

    Raises:
        ValueError: If parameters are out of valid ranges
    """
    if hdl_cholesterol >= total_cholesterol:
        raise ValueError("HDL cholesterol must be lower than total cholesterol")
    if hdl_cholesterol > 10:
        # TODO: automatically calculate with mg/dl?
        raise ValueError(f"HDL cholesterol ({hdl_cholesterol}) is implausible high. Did you provide mg/dl instead of mmol/l?")
    if total_cholesterol > 30:
        # TODO: automatically calculate with mg/dl?
        raise ValueError(f"Total cholesterol ({total_cholesterol}) is implausible high. Did you provide mg/dl instead of mmol/l?")
    if not 30 <= age <= 79:
        raise ValueError("Age must be between 30 and 79 years")
    if total_cholesterol < 0:
        raise ValueError("Total cholesterol must be non-negative")
    if hdl_cholesterol < 0:
        raise ValueError("HDL cholesterol must be non-negative")
    if systolic_bp < 0:
        raise ValueError("Systolic BP must be non-negative")

    points = 0

    # Age points
    if gender == Gender.MALE:
        if age >= 75:
            points += 15
        elif age >= 70:
            points += 14
        elif age >= 65:
            points += 12
        elif age >= 60:
            points += 11
        elif age >= 55:
            points += 10
        elif age >= 50:
            points += 8
        elif age >= 45:
            points += 6
        elif age >= 40:
            points += 5
        elif age >= 35:
            points += 2
        else:  # 30-34
            pass
    else:  # Female
        if age >= 75:
            points += 12
        elif age >= 70:
            points += 11
        elif age >= 65:
            points += 10
        elif age >= 60:
            points += 9
        elif age >= 55:
            points += 8
        elif age >= 50:
            points += 7
        elif age >= 45:
            points += 5
        elif age >= 40:
            points += 4
        elif age >= 35:
            points += 2
        else:  # 30-34
            pass

    # Total cholesterol points
    if total_cholesterol < 4.1:
        pass
    elif 4.1 <= total_cholesterol < 5.20:
        points += 1
    elif 5.20 <= total_cholesterol < 6.2:
        points += 2 if gender == Gender.MALE else 3
    elif 6.2 <= total_cholesterol < 7.2:
        points += 3 if gender == Gender.MALE else 4
    else:  # chol > 7.2 mmol/l
        points += 4 if gender == Gender.MALE else 5

    # HDL cholesterol points
    if hdl_cholesterol > 1.6:
        points -= 2
    elif 1.3 <= hdl_cholesterol <= 1.6:
        points -= 1
    elif 1.2 <= hdl_cholesterol < 1.3:
        points -= 1
    elif 0.9 <= hdl_cholesterol < 1.2:
        points -= 1
    elif hdl_cholesterol < 0.9:
        points += 2

    # Blood pressure points
    if bp_treatment:
        if systolic_bp >= 160:
            points += 5 if gender == Gender.MALE else 7
        elif 150 <= systolic_bp < 160:
            points += 4 if gender == Gender.MALE else 6
        elif 140 <= systolic_bp < 150:
            points += 4 if gender == Gender.MALE else 5
        elif 130 <= systolic_bp < 140:
            points += 3
        elif 120 <= systolic_bp < 130:
            points += 2
        elif systolic_bp < 120:
            points += 0 if gender == Gender.MALE else -1
    else:
        if systolic_bp >= 160:
            points += 3 if gender == Gender.MALE else 5
        elif 150 <= systolic_bp < 160:
            points += 2 if gender == Gender.MALE else 4
        elif 140 <= systolic_bp < 150:
            points += 2
        elif 130 <= systolic_bp < 140:
            points += 1
        elif 120 <= systolic_bp < 130:
            points += 0
        elif systolic_bp < 120:
            points += -2 if gender == Gender.MALE else -3
        # < 120: 0 points

    # Smoking points
    if smoking:
        points += 4 if gender == Gender.MALE else 3

    # Diabetes points
    if diabetes:
        points += 3 if gender == Gender.MALE else 4

    # Calculate 10-year risk percentage
    # hint: 0.999 means "<1", 30 means ">30"
    if gender == Gender.MALE:
        risk_table = {
            -3: 0.999,  # below 1%
            -2: 1.1,
            -1: 1.4,
            0: 1.6,
            1: 1.9,
            2: 2.3,
            3: 2.8,
            4: 3.3,
            5: 3.9,
            6: 4.7,
            7: 5.6,
            8: 6.7,
            9: 7.9,
            10: 9.4,
            11: 11.2,
            12: 13.2,
            13: 15.6,
            14: 18.4,
            15: 21.4,
            16: 25.3,
            17: 29.4,
            18: 30,  # >30
            19: 30,  # >30
            20: 30,  # >30
            21: 30,  # >30
        }
    else:
        risk_table = {
            -3: 1,  # below 1%
            -2: 1,  # below 1%
            -1: 1.0,
            0: 1.2,
            1: 1.5,
            2: 1.7,
            3: 2.0,
            4: 2.4,
            5: 2.8,
            6: 3.3,
            7: 3.9,
            8: 4.5,
            9: 5.3,
            10: 6.3,
            11: 7.3,
            12: 8.6,
            13: 10.0,
            14: 11.7,
            15: 13.7,
            16: 15.9,
            17: 18.5,
            18: 21.5,
            19: 24.8,
            20: 28.5,
            21: 30,  # >30
        }

    # Get risk percentage (cap at table limits)
    risk_points = min(max(points, min(risk_table.keys())), max(risk_table.keys()))
    risk_percentage = risk_table.get(risk_points)

    # Determine risk level
    if risk_percentage < 10:
        risk_level = FraminghamRiskLevel.LOW
    elif risk_percentage < 20:
        risk_level = FraminghamRiskLevel.INTERMEDIATE
    else:
        risk_level = FraminghamRiskLevel.HIGH

    return points, float(risk_percentage), risk_level
