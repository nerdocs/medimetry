import pytest

from medimetry import Gender
from medimetry.cardiovasc import FraminghamRiskLevel
from medimetry.cardiovasc import framingham_category
from medimetry.cardiovasc import framingham_risk
from medimetry.cardiovasc import framingham_score

# Point and risk tables: D'Agostino RB Sr, et al. Circulation. 2008;117(6):743-753, Table 5 (CVD points for women),
# Table 6 (10-year CVD risk for women), Table 7 (CVD points for men), Table 8 (10-year CVD risk for men). The paper's
# full text was not accessible when these tests were written; the tables were read from a verbatim reproduction that
# cites them (Novartis statistical analysis plan, study CABL001J12301, SAP Amendment 2, section 5.5.1, Tables 5-3 to
# 5-6, clinicaltrials.gov NCT04971226).

# Baseline that contributes 0 points for both sexes: TC 4.0 mmol/l (< 160 mg/dl), HDL 1.2 mmol/l (45-49 mg/dl),
# untreated SBP 125 mmHg (120-129), non-smoker, no diabetes.
BASELINE = {"total_cholesterol": 4.0, "hdl_cholesterol": 1.2, "systolic_bp": 125}


def _framingham(**kwargs):
    points = framingham_score(**kwargs)
    risk = framingham_risk(points, kwargs["gender"])
    return points, risk, framingham_category(risk)


def test_framingham_score_hdl_greater_than_total_cholesterol():
    """Test that ValueError is raised when HDL cholesterol is greater than total cholesterol."""
    with pytest.raises(ValueError, match="HDL cholesterol must be lower than total cholesterol"):
        framingham_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=4.0,
            hdl_cholesterol=5.0,
            systolic_bp=120,
        )


def test_framingham_score_hdl_equals_total_cholesterol():
    """Test that ValueError is raised when HDL cholesterol is greater than total cholesterol."""
    with pytest.raises(ValueError, match="HDL cholesterol must be lower than total cholesterol"):
        framingham_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=4.0,
            hdl_cholesterol=4.0,
            systolic_bp=120,
        )


def test_framingham_score_hdl_exceeds_10_mmol():
    """Test that ValueError is raised when HDL cholesterol exceeds 10 mmol/l."""
    with pytest.raises(
        ValueError,
        match=r"HDL cholesterol .* is implausible high. Did "
        "you provide mg/dl instead of mmol/l\\?",
    ):
        framingham_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=20.0,
            hdl_cholesterol=15.0,
            systolic_bp=120,
        )


def test_framingham_score_total_cholesterol_exceeds_30_mmol():
    """Test that ValueError is raised when total cholesterol exceeds 30 mmol/l."""
    with pytest.raises(
        ValueError,
        match=r"Total cholesterol .* is implausible high. Did you provide "
        r"mg/dl instead of mmol/l\\?",
    ):
        framingham_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=35.0,
            hdl_cholesterol=1.5,
            systolic_bp=120,
        )


def test_framingham_score_age_above_79():
    """Test that ValueError is raised when age is above 79 years."""
    with pytest.raises(ValueError, match="Age must be between 30 and 79 years"):
        framingham_score(
            age=80,
            gender=Gender.MALE,
            total_cholesterol=5.0,
            hdl_cholesterol=1.2,
            systolic_bp=120,
        )


def test_framingham_score_negative_total_cholesterol():
    """Test that ValueError is raised when total cholesterol is negative."""
    with pytest.raises(ValueError, match="Total cholesterol must be non-negative"):
        framingham_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=-1.0,
            hdl_cholesterol=1.2,
            systolic_bp=120,
        )


def test_framingham_score_negative_hdl_cholesterol():
    """Test that ValueError is raised when HDL cholesterol is negative."""
    with pytest.raises(ValueError, match="HDL cholesterol must be non-negative"):
        framingham_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=5.0,
            hdl_cholesterol=-1.0,
            systolic_bp=120,
        )


def test_framingham_score_negative_systolic_bp():
    """Test that ValueError is raised when systolic blood pressure is negative."""
    with pytest.raises(ValueError, match="Systolic BP must be non-negative"):
        framingham_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=5.0,
            hdl_cholesterol=1.2,
            systolic_bp=-10,
        )


def test_framingham_score_male_minimum_age_no_risk_factors():
    """Test Framingham risk score for 30-year-old male with no risk factors."""
    points, risk_percentage, risk_level = _framingham(
        age=30,
        gender=Gender.MALE,
        total_cholesterol=4.0,  # < 160 mg/dl (4.14 mmol/l): 0 points
        hdl_cholesterol=1.7,  # Above 1.6 mmol/l (-2 points)
        systolic_bp=110,  # Below 120 mmHg (-2 points)
        bp_treatment=False,
        smoking=False,
        diabetes=False,
    )
    # Age 30-34: 0 points
    # Total cholesterol <4.1: 0 points
    # HDL >1.6: -2 points
    # SBP <120 (untreated): -2 points
    # No smoking: 0 points
    # No diabetes: 0 points
    # Total: -4 points, but capped at minimum table value
    assert points == -4
    assert risk_percentage == 0.999  # <1% risk
    assert risk_level == FraminghamRiskLevel.LOW


def test_framingham_score_female_maximum_age_all_risk_factors():
    """Test Framingham risk score for 79-year-old female with all risk factors."""
    points, risk_percentage, risk_level = _framingham(
        age=79,
        gender=Gender.FEMALE,
        total_cholesterol=8.0,  # >= 280 mg/dl (7.24 mmol/l): 5 points
        hdl_cholesterol=0.8,  # <0.9 mmol/l (2 points)
        systolic_bp=170,  # >=160 mmHg treated (7 points)
        bp_treatment=True,
        smoking=True,  # 3 points
        diabetes=True,  # 4 points
    )
    # Age 75-79: 12 points
    # Total cholesterol >7.2: 5 points
    # HDL <0.9: 2 points
    # SBP >=160 (treated): 7 points
    # Smoking: 3 points
    # Diabetes: 4 points
    # Total: 33 points, but capped at table maximum (21)
    assert points == 33
    assert risk_percentage == 30.0  # >30% risk (capped)
    assert risk_level == FraminghamRiskLevel.HIGH


def test_framingham_score_middle_aged_female_moderate_risk():
    """Test Framingham risk score for middle-aged female with moderate risk factors."""
    points, risk_percentage, risk_level = _framingham(
        age=55,
        gender=Gender.FEMALE,
        total_cholesterol=5.5,  # 200-239 mg/dl: 3 points
        hdl_cholesterol=1.1,  # 0.9-1.2 mmol/l (+1 point)
        systolic_bp=145,  # 140-150 mmHg untreated (2 points)
        bp_treatment=False,
        smoking=True,  # 3 points
        diabetes=False,
    )
    # Age 55-59: 8 points
    # Total cholesterol 5.20-6.2: 3 points
    # HDL 0.9-1.2: +1 point
    # SBP 140-150 (untreated): 2 points
    # Smoking: 3 points
    # No diabetes: 0 points
    # Total: 17 points
    assert points == 17
    assert risk_percentage == 18.5  # 18.5% risk
    assert risk_level == FraminghamRiskLevel.INTERMEDIATE


@pytest.mark.parametrize(
    ("hdl", "expected_points"),
    [
        (1.6, -2),  # >= 60 mg/dl (1.55 mmol/l)
        (1.55, -1),  # 50-59 mg/dl
        (1.3, -1),
        (1.25, 0),  # 45-49 mg/dl
        (1.17, 0),
        (1.16, 1),  # 35-44 mg/dl
        (0.91, 1),
        (0.9, 2),  # < 35 mg/dl (0.905 mmol/l)
    ],
)
def test_framingham_hdl_bands(hdl, expected_points):
    """HDL point bands per D'Agostino 2008, Table 4: -2, -1, 0, +1, +2."""
    # Baseline: male, 30 y (0), TC 4.0 (0), SBP 125 untreated (0) -> only HDL contributes
    points = framingham_score(age=30, gender=Gender.MALE, total_cholesterol=4.0, hdl_cholesterol=hdl, systolic_bp=125)
    assert points == expected_points


@pytest.mark.parametrize(
    ("tc", "expected_points"),
    [
        (4.13, 0),  # < 160 mg/dl (4.14 mmol/l)
        (4.14, 1),  # 160-199 mg/dl
        (5.17, 1),
        (5.18, 2),  # 200-239 mg/dl (5.17 mmol/l)
        (6.20, 2),
        (6.21, 3),  # 240-279 mg/dl (6.21 mmol/l)
        (7.24, 3),
        (7.25, 4),  # >= 280 mg/dl (7.24 mmol/l)
    ],
)
def test_framingham_total_cholesterol_bands(tc, expected_points):
    """Male total cholesterol point bands per D'Agostino 2008, Table 4: 0, +1, +2, +3, +4."""
    # Baseline: male, 30 y (0), HDL 1.2 (0), SBP 125 untreated (0) -> only TC contributes
    points = framingham_score(age=30, gender=Gender.MALE, total_cholesterol=tc, hdl_cholesterol=1.2, systolic_bp=125)
    assert points == expected_points


def test_framingham_paper_example_female():
    """Worked example from D'Agostino 2008: 61-year-old woman, TC 180 mg/dl (4.66 mmol/l), HDL 47 mg/dl (1.22 mmol/l),
    untreated SBP 124 mmHg, smoker, no diabetes -> 13 points, 10.0 %."""
    points, risk, level = _framingham(
        age=61, gender=Gender.FEMALE, total_cholesterol=4.66, hdl_cholesterol=1.22, systolic_bp=124, smoking=True
    )
    # age 60-64: 9, TC 160-199 mg/dl: 1, HDL 45-49 mg/dl: 0, SBP 120-129 untreated: 0, smoker: 3
    assert points == 13
    assert risk == 10.0
    assert level == FraminghamRiskLevel.INTERMEDIATE


@pytest.mark.parametrize(
    ("age", "expected_points"),
    [
        *[(30, 0), (34, 0), (35, 2), (39, 2), (40, 5), (44, 5), (45, 6), (49, 6), (50, 8), (54, 8), (55, 10), (59, 10)],
        *[(60, 11), (64, 11), (65, 12), (69, 12), (70, 14), (74, 14), (75, 15), (79, 15)],
    ],
)
def test_framingham_male_age_bands(age, expected_points):
    """Male age points per D'Agostino 2008, Table 7: 30-34 0, 35-39 2, 40-44 5, 45-49 6, 50-54 8, 55-59 10,
    60-64 11, 65-69 12, 70-74 14, 75+ 15."""
    assert framingham_score(age=age, gender=Gender.MALE, **BASELINE) == expected_points


@pytest.mark.parametrize(
    ("age", "expected_points"),
    [(30, 0), (35, 2), (40, 4), (45, 5), (50, 7), (55, 8), (60, 9), (65, 10), (70, 11), (75, 12), (79, 12)],
)
def test_framingham_female_age_bands(age, expected_points):
    """Female age points per D'Agostino 2008, Table 5: 30-34 0, 35-39 2, 40-44 4, 45-49 5, 50-54 7, 55-59 8,
    60-64 9, 65-69 10, 70-74 11, 75+ 12."""
    assert framingham_score(age=age, gender=Gender.FEMALE, **BASELINE) == expected_points


@pytest.mark.parametrize(
    ("sbp", "expected_points"),
    [(119, 0), (120, 2), (129, 2), (130, 3), (139, 3), (140, 4), (159, 4), (160, 5), (200, 5)],
)
def test_framingham_male_treated_sbp_bands(sbp, expected_points):
    """Male treated SBP points per D'Agostino 2008, Table 7: < 120 0, 120-129 2, 130-139 3, 140-159 4, 160+ 5."""
    kwargs = {**BASELINE, "systolic_bp": sbp}
    assert framingham_score(age=30, gender=Gender.MALE, bp_treatment=True, **kwargs) == expected_points


@pytest.mark.parametrize(
    ("sbp", "expected_points"),
    [(119, -2), (120, 0), (129, 0), (130, 1), (139, 1), (140, 2), (159, 2), (160, 3)],
)
def test_framingham_male_untreated_sbp_bands(sbp, expected_points):
    """Male untreated SBP points per D'Agostino 2008, Table 7: < 120 -2, 120-129 0, 130-139 1, 140-159 2, 160+ 3."""
    kwargs = {**BASELINE, "systolic_bp": sbp}
    assert framingham_score(age=30, gender=Gender.MALE, **kwargs) == expected_points


@pytest.mark.parametrize(
    ("sbp", "expected_points"),
    [(119, -1), (120, 2), (129, 2), (130, 3), (139, 3), (140, 5), (149, 5), (150, 6), (159, 6), (160, 7)],
)
def test_framingham_female_treated_sbp_bands(sbp, expected_points):
    """Female treated SBP points per D'Agostino 2008, Table 5: < 120 -1, 120-129 2, 130-139 3, 140-149 5,
    150-159 6, 160+ 7."""
    kwargs = {**BASELINE, "systolic_bp": sbp}
    assert framingham_score(age=30, gender=Gender.FEMALE, bp_treatment=True, **kwargs) == expected_points


@pytest.mark.parametrize(
    ("sbp", "expected_points"),
    [(119, -3), (120, 0), (130, 1), (140, 2), (149, 2), (150, 4), (159, 4), (160, 5)],
)
def test_framingham_female_untreated_sbp_bands(sbp, expected_points):
    """Female untreated SBP points per D'Agostino 2008, Table 5: < 120 -3, 120-129 0, 130-139 1, 140-149 2,
    150-159 4, 160+ 5."""
    kwargs = {**BASELINE, "systolic_bp": sbp}
    assert framingham_score(age=30, gender=Gender.FEMALE, **kwargs) == expected_points


def test_framingham_smoker_and_diabetes_points():
    """Smoker / diabetic per D'Agostino 2008: men 4 / 3 (Table 7), women 3 / 4 (Table 5)."""
    assert framingham_score(age=30, gender=Gender.MALE, smoking=True, **BASELINE) == 4
    assert framingham_score(age=30, gender=Gender.MALE, diabetes=True, **BASELINE) == 3
    assert framingham_score(age=30, gender=Gender.FEMALE, smoking=True, **BASELINE) == 3
    assert framingham_score(age=30, gender=Gender.FEMALE, diabetes=True, **BASELINE) == 4


def test_framingham_female_example_from_reproduction():
    """Worked example of the SAP reproduction (section 5.5.1.1): woman, 43 y (+4), HDL 65 mg/dl (-2), TC 150 mg/dl (0),
    treated SBP 125 mmHg (+2), smoker (+3), no diabetes -> 7 points."""
    points = framingham_score(
        age=43,
        gender=Gender.FEMALE,
        total_cholesterol=150 / 38.67,
        hdl_cholesterol=65 / 38.67,
        systolic_bp=125,
        bp_treatment=True,
        smoking=True,
    )
    assert points == 7


MALE_RISK = {-2: 1.1, -1: 1.4, 0: 1.6, 1: 1.9, 2: 2.3, 3: 2.8, 4: 3.3, 5: 3.9, 6: 4.7, 7: 5.6, 8: 6.7, 9: 7.9, 10: 9.4}
MALE_RISK |= {11: 11.2, 12: 13.2, 13: 15.6, 14: 18.4, 15: 21.6, 16: 25.3, 17: 29.4}
FEMALE_RISK = {-1: 1.0, 0: 1.2, 1: 1.5, 2: 1.7, 3: 2.0, 4: 2.4, 5: 2.8, 6: 3.3, 7: 3.9, 8: 4.5, 9: 5.3, 10: 6.3}
FEMALE_RISK |= {11: 7.3, 12: 8.6, 13: 10.0, 14: 11.7, 15: 13.7, 16: 15.9, 17: 18.5, 18: 21.5, 19: 24.8, 20: 28.5}


@pytest.mark.parametrize(("points", "risk"), MALE_RISK.items())
def test_framingham_male_risk_table(points, risk):
    """10-year CVD risk for men per D'Agostino 2008, Table 8."""
    assert framingham_risk(points, Gender.MALE) == risk


@pytest.mark.parametrize(("points", "risk"), FEMALE_RISK.items())
def test_framingham_female_risk_table(points, risk):
    """10-year CVD risk for women per D'Agostino 2008, Table 6."""
    assert framingham_risk(points, Gender.FEMALE) == risk


def test_framingham_risk_open_ends():
    """ "< 1 %" (men <= -3, women <= -2) is returned as 0.999, "> 30 %" (men >= 18, women >= 21) as 30.0."""
    assert framingham_risk(-3, Gender.MALE) == framingham_risk(-10, Gender.MALE) == 0.999
    assert framingham_risk(-2, Gender.FEMALE) == framingham_risk(-10, Gender.FEMALE) == 0.999
    assert framingham_risk(18, Gender.MALE) == framingham_risk(40, Gender.MALE) == 30.0
    assert framingham_risk(21, Gender.FEMALE) == framingham_risk(40, Gender.FEMALE) == 30.0


def test_framingham_risk_validation():
    with pytest.raises(TypeError, match="must be an int"):
        framingham_risk(5.0, Gender.MALE)
    with pytest.raises(TypeError, match="must be an int"):
        framingham_risk(True, Gender.MALE)
    with pytest.raises(ValueError, match="Gender"):
        framingham_risk(5, Gender.DIVERSE)


@pytest.mark.parametrize(
    ("risk", "level"),
    [
        (0.999, FraminghamRiskLevel.LOW),
        (9.9, FraminghamRiskLevel.LOW),
        (10.0, FraminghamRiskLevel.INTERMEDIATE),
        (19.9, FraminghamRiskLevel.INTERMEDIATE),
        (20.0, FraminghamRiskLevel.HIGH),
        (30.0, FraminghamRiskLevel.HIGH),
    ],
)
def test_framingham_category_bands(risk, level):
    """Risk levels per CCS 2016 (Anderson 2016): < 10 % low, 10-19.9 % intermediate, >= 20 % high."""
    assert framingham_category(risk) == level


@pytest.mark.parametrize("risk", [-0.1, 100.1])
def test_framingham_category_out_of_range(risk):
    with pytest.raises(ValueError, match="between 0 and 100"):
        framingham_category(risk)
