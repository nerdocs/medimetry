from enum import Enum

from medimetry import Gender
from medimetry._formula import FormulaInfo
from medimetry._formula import half_up


class FraminghamRiskLevel(Enum):
    """Framingham risk level categories (CCS 2016: < 10 %, 10-19.9 %, >= 20 %)."""

    LOW = "low"
    INTERMEDIATE = "intermediate"
    HIGH = "high"


def mean_arterial_pressure(systolic: float, diastolic: float, *, rounded: bool = False) -> float:
    """
    Calculate mean arterial pressure (MAP) from systolic and diastolic blood pressure.

    MAP = (2 x diastolic + systolic) / 3

    Args:
        systolic (float): Systolic blood pressure in mm Hg
        diastolic (float): Diastolic blood pressure in mm Hg
        rounded (bool): Round to ``MEAN_ARTERIAL_PRESSURE.digits`` places (half up)

    Returns:
        float: Mean arterial pressure in mm Hg
    Raises:
        ValueError: If either systolic or diastolic pressure is not positive or diastolic
        is not lower than systolic.
    """
    if systolic <= 0:
        raise ValueError(f"Systolic pressure must be positive: {systolic}")
    if diastolic <= 0:
        raise ValueError(f"Diastolic pressure must be positive: {diastolic}")
    if diastolic >= systolic:
        raise ValueError(f"Diastolic pressure must be lower than systolic pressure: diastolic={diastolic}, systolic={systolic}")

    value = (2 * diastolic + systolic) / 3
    return half_up(value, MEAN_ARTERIAL_PRESSURE.digits) if rounded else value


MEAN_ARTERIAL_PRESSURE = FormulaInfo(
    id="mean_arterial_pressure",
    name="Mean arterial pressure",
    function=mean_arterial_pressure,
    unit="mm[Hg]",
    inputs={"systolic": "mm[Hg]", "diastolic": "mm[Hg]"},
    digits=1,
    citation="Standard approximation (2 x diastolic + systolic) / 3; no single primary source",
    loinc="8478-0",
)


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
    Calculate the CHA2DS2-VASc score as published by Lip et al. (2010).

    References:
        Lip GY, et al. Refining clinical risk stratification for predicting stroke and
        thromboembolism in atrial fibrillation using a novel risk factor-based approach:
        the Euro Heart Survey on Atrial Fibrillation. Chest. 2010;137(2):263-272.
        doi:10.1378/chest.09-1584

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
        raise ValueError(f"Age must be positive: {age}")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError(f"Gender must be Gender.MALE or Gender.FEMALE: {gender}")

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


def framingham_score(
    age: int,
    gender: Gender,
    total_cholesterol: float,
    hdl_cholesterol: float,
    systolic_bp: int,
    bp_treatment: bool = False,
    smoking: bool = False,
    diabetes: bool = False,
) -> int:
    """
    Calculate the Framingham General Cardiovascular Disease points (10-year risk profile, lipid version).

    This is the sex-specific points system of the 2008 Framingham General CVD risk
    profile, not the older ATP III hard-CHD score. The points are converted to a 10-year
    risk with ``framingham_risk``; the risk level is a separate step (``framingham_category``).

    References:
        D'Agostino RB Sr, et al. General cardiovascular risk profile for use in primary care:
        the Framingham Heart Study. Circulation. 2008;117(6):743-753.
        doi:10.1161/CIRCULATIONAHA.107.699579 (CVD points: Table 5 women, Table 7 men)

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
        int: Sum of the CVD points (not capped to the range of the risk table)

    Raises:
        ValueError: If parameters are out of valid ranges

    >>> framingham_score(age=61, gender=Gender.FEMALE, total_cholesterol=4.66, hdl_cholesterol=1.22, systolic_bp=124, smoking=True)
    13
    """
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError(f"Gender must be Gender.MALE or Gender.FEMALE: {gender}")
    if not 30 <= age <= 79:
        raise ValueError(f"Age must be between 30 and 79 years: {age}")
    if total_cholesterol < 0:
        raise ValueError(f"Total cholesterol must be non-negative: {total_cholesterol}")
    if hdl_cholesterol < 0:
        raise ValueError(f"HDL cholesterol must be non-negative: {hdl_cholesterol}")
    if systolic_bp < 0:
        raise ValueError(f"Systolic BP must be non-negative: {systolic_bp}")
    if hdl_cholesterol >= total_cholesterol:
        raise ValueError(
            f"HDL cholesterol must be lower than total cholesterol: hdl_cholesterol={hdl_cholesterol}, total_cholesterol={total_cholesterol}"
        )
    if hdl_cholesterol > 10:
        raise ValueError(f"HDL cholesterol ({hdl_cholesterol}) is implausible high. Did you provide mg/dl instead of mmol/l?")
    if total_cholesterol > 30:
        raise ValueError(f"Total cholesterol ({total_cholesterol}) is implausible high. Did you provide mg/dl instead of mmol/l?")

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

    # Total cholesterol points, bands as published in mg/dl
    total_cholesterol_mg_dl = total_cholesterol * 38.67
    if total_cholesterol_mg_dl < 160:
        pass
    elif total_cholesterol_mg_dl < 200:
        points += 1
    elif total_cholesterol_mg_dl < 240:
        points += 2 if gender == Gender.MALE else 3
    elif total_cholesterol_mg_dl < 280:
        points += 3 if gender == Gender.MALE else 4
    else:
        points += 4 if gender == Gender.MALE else 5

    # HDL cholesterol points (same for both sexes), bands as published in mg/dl
    hdl_mg_dl = hdl_cholesterol * 38.67
    if hdl_mg_dl >= 60:
        points -= 2
    elif hdl_mg_dl >= 50:
        points -= 1
    elif hdl_mg_dl >= 45:
        points += 0
    elif hdl_mg_dl >= 35:
        points += 1
    else:
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

    return points


def framingham_risk(points: int, gender: Gender) -> float:
    """
    Convert Framingham General CVD points into the published 10-year CVD risk in percent.

    The tables are open-ended: 0.999 stands for "< 1 %" (men <= -3, women <= -2 points),
    30.0 for "> 30 %" (men >= 18, women >= 21 points).

    References:
        D'Agostino RB Sr, et al. General cardiovascular risk profile for use in primary care:
        the Framingham Heart Study. Circulation. 2008;117(6):743-753.
        doi:10.1161/CIRCULATIONAHA.107.699579 (10-year CVD risk: Table 6 women, Table 8 men)

    Args:
        points (int): CVD points, e.g. from ``framingham_score``
        gender (Gender): Gender (Gender.MALE or Gender.FEMALE)

    Returns:
        float: 10-year CVD risk in percent, as tabulated

    Raises:
        TypeError: If points is not an int
        ValueError: If gender is not Gender.MALE or Gender.FEMALE

    >>> framingham_risk(13, Gender.FEMALE)
    10.0
    """
    if not isinstance(points, int) or isinstance(points, bool):
        raise TypeError(f"Framingham points must be an int: {points!r}")
    if gender not in (Gender.MALE, Gender.FEMALE):
        raise ValueError(f"Gender must be Gender.MALE or Gender.FEMALE: {gender}")

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
            15: 21.6,
            16: 25.3,
            17: 29.4,
            18: 30,  # >30
            19: 30,  # >30
            20: 30,  # >30
            21: 30,  # >30
        }
    else:
        risk_table = {
            -3: 0.999,  # below 1%
            -2: 0.999,  # below 1%
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

    risk_points = min(max(points, min(risk_table.keys())), max(risk_table.keys()))
    return float(risk_table[risk_points])


def framingham_category(risk_percentage: float) -> FraminghamRiskLevel:
    """
    Return the risk level of a Framingham 10-year CVD risk: low < 10 %, intermediate 10-19.9 %, high >= 20 %.

    The levels are not part of D'Agostino 2008; they are a guideline convention.

    References:
        Anderson TJ, et al. 2016 Canadian Cardiovascular Society Guidelines for the Management
        of Dyslipidemia for the Prevention of Cardiovascular Disease in the Adult.
        Can J Cardiol. 2016;32(11):1263-1282. doi:10.1016/j.cjca.2016.07.510

    Args:
        risk_percentage (float): 10-year CVD risk in percent, e.g. from ``framingham_risk``

    Returns:
        FraminghamRiskLevel: Risk level

    Raises:
        ValueError: If risk_percentage is outside 0-100

    >>> framingham_category(10.0)
    <FraminghamRiskLevel.INTERMEDIATE: 'intermediate'>
    """
    if not 0 <= risk_percentage <= 100:
        raise ValueError(f"Risk percentage must be between 0 and 100: {risk_percentage}")
    if risk_percentage < 10:
        return FraminghamRiskLevel.LOW
    if risk_percentage < 20:
        return FraminghamRiskLevel.INTERMEDIATE
    return FraminghamRiskLevel.HIGH
