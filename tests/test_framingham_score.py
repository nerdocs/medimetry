import pytest

from medimetry import Gender
from medimetry.cardiovasc import FraminghamRiskLevel
from medimetry.cardiovasc import framingham_risk_score


def test_framingham_risk_score_hdl_greater_than_total_cholesterol():
    """Test that ValueError is raised when HDL cholesterol is greater than total cholesterol."""
    with pytest.raises(ValueError, match="HDL cholesterol must be lower than total cholesterol"):
        framingham_risk_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=4.0,
            hdl_cholesterol=5.0,
            systolic_bp=120,
        )


def test_framingham_risk_score_hdl_equals_total_cholesterol():
    """Test that ValueError is raised when HDL cholesterol is greater than total cholesterol."""
    with pytest.raises(ValueError, match="HDL cholesterol must be lower than total cholesterol"):
        framingham_risk_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=4.0,
            hdl_cholesterol=4.0,
            systolic_bp=120,
        )


def test_framingham_risk_score_hdl_exceeds_10_mmol():
    """Test that ValueError is raised when HDL cholesterol exceeds 10 mmol/l."""
    with pytest.raises(
        ValueError,
        match=r"HDL cholesterol .* is implausible high. Did "
        "you provide mg/dl instead of mmol/l\\?",
    ):
        framingham_risk_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=20.0,
            hdl_cholesterol=15.0,
            systolic_bp=120,
        )


def test_framingham_risk_score_total_cholesterol_exceeds_30_mmol():
    """Test that ValueError is raised when total cholesterol exceeds 30 mmol/l."""
    with pytest.raises(
        ValueError,
        match=r"Total cholesterol .* is implausible high. Did you provide "
        r"mg/dl instead of mmol/l\\?",
    ):
        framingham_risk_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=35.0,
            hdl_cholesterol=1.5,
            systolic_bp=120,
        )


def test_framingham_risk_score_age_above_79():
    """Test that ValueError is raised when age is above 79 years."""
    with pytest.raises(ValueError, match="Age must be between 30 and 79 years"):
        framingham_risk_score(
            age=80,
            gender=Gender.MALE,
            total_cholesterol=5.0,
            hdl_cholesterol=1.2,
            systolic_bp=120,
        )


def test_framingham_risk_score_negative_total_cholesterol():
    """Test that ValueError is raised when total cholesterol is negative."""
    with pytest.raises(ValueError, match="Total cholesterol must be non-negative"):
        framingham_risk_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=-1.0,
            hdl_cholesterol=1.2,
            systolic_bp=120,
        )


def test_framingham_risk_score_negative_hdl_cholesterol():
    """Test that ValueError is raised when HDL cholesterol is negative."""
    with pytest.raises(ValueError, match="HDL cholesterol must be non-negative"):
        framingham_risk_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=5.0,
            hdl_cholesterol=-1.0,
            systolic_bp=120,
        )


def test_framingham_risk_score_negative_systolic_bp():
    """Test that ValueError is raised when systolic blood pressure is negative."""
    with pytest.raises(ValueError, match="Systolic BP must be non-negative"):
        framingham_risk_score(
            age=50,
            gender=Gender.MALE,
            total_cholesterol=5.0,
            hdl_cholesterol=1.2,
            systolic_bp=-10,
        )


def test_framingham_risk_score_male_minimum_age_no_risk_factors():
    """Test Framingham risk score for 30-year-old male with no risk factors."""
    points, risk_percentage, risk_level = framingham_risk_score(
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


def test_framingham_risk_score_female_maximum_age_all_risk_factors():
    """Test Framingham risk score for 79-year-old female with all risk factors."""
    points, risk_percentage, risk_level = framingham_risk_score(
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


def test_framingham_risk_score_middle_aged_female_moderate_risk():
    """Test Framingham risk score for middle-aged female with moderate risk factors."""
    points, risk_percentage, risk_level = framingham_risk_score(
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
    points, _, _ = framingham_risk_score(age=30, gender=Gender.MALE, total_cholesterol=4.0, hdl_cholesterol=hdl, systolic_bp=125)
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
    points, _, _ = framingham_risk_score(age=30, gender=Gender.MALE, total_cholesterol=tc, hdl_cholesterol=1.2, systolic_bp=125)
    assert points == expected_points


def test_framingham_paper_example_female():
    """Worked example from D'Agostino 2008: 61-year-old woman, TC 180 mg/dl (4.66 mmol/l), HDL 47 mg/dl (1.22 mmol/l),
    untreated SBP 124 mmHg, smoker, no diabetes -> 13 points, 10.0 %."""
    points, risk, level = framingham_risk_score(
        age=61, gender=Gender.FEMALE, total_cholesterol=4.66, hdl_cholesterol=1.22, systolic_bp=124, smoking=True
    )
    # age 60-64: 9, TC 160-199 mg/dl: 1, HDL 45-49 mg/dl: 0, SBP 120-129 untreated: 0, smoker: 3
    assert points == 13
    assert risk == 10.0
    assert level == FraminghamRiskLevel.INTERMEDIATE
