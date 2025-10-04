import pytest

from medimetry.pulmonary import GenevaRiskLevel
from medimetry.pulmonary import geneva_revised_score
from medimetry.pulmonary import geneva_score


def test_geneva_score_minimal_case():
    """Test Geneva score with minimal risk factors."""
    result = geneva_score(age=30)

    assert result.score == 0
    assert result.risk_level == GenevaRiskLevel.LOW
    assert result.pe_probability == "8%"


def test_geneva_score_age_scoring():
    """Test Geneva score age-based scoring."""
    # Age < 60: 0 points
    result = geneva_score(age=50)
    assert result.score == 0

    # Age 60-79: 1 point
    result = geneva_score(age=70)
    assert result.score == 1

    # Age >= 80: 2 points
    result = geneva_score(age=85)
    assert result.score == 2


def test_geneva_score_all_factors():
    """Test Geneva score with all risk factors present."""
    result = geneva_score(
        age=85,  # 2 points
        previous_pe_dvt=True,  # 1 point
        heart_rate_over_100=True,  # 1 point
        recent_surgery=True,  # 1 point
        hemoptysis=True,  # 1 point
        active_cancer=True,  # 1 point
        unilateral_leg_pain=True,  # 1 point
        unilateral_leg_edema=True,  # 1 point
        pain_on_palpation=True,  # 1 point
    )

    assert result.score == 10
    assert result.risk_level == GenevaRiskLevel.HIGH
    assert result.pe_probability == "74%"


def test_geneva_score_risk_levels():
    """Test Geneva score risk level classification."""
    # Low risk (0-3 points)
    result = geneva_score(age=70, previous_pe_dvt=True, heart_rate_over_100=True)
    assert result.score == 3
    assert result.risk_level == GenevaRiskLevel.LOW

    # Intermediate risk (4-8 points)
    result = geneva_score(
        age=70,  # 1 point
        previous_pe_dvt=True,  # 1 point
        heart_rate_over_100=True,  # 1 point
        recent_surgery=True,  # 1 point
        hemoptysis=True,  # 1 point
        active_cancer=True,  # 1 point
        unilateral_leg_pain=True,  # 1 point
        unilateral_leg_edema=True,  # 1 point
    )
    assert result.score == 8
    assert result.risk_level == GenevaRiskLevel.INTERMEDIATE

    # High risk (>8 points)
    result = geneva_score(
        age=85,  # 2 points
        previous_pe_dvt=True,  # 1 point
        heart_rate_over_100=True,  # 1 point
        recent_surgery=True,  # 1 point
        hemoptysis=True,  # 1 point
        active_cancer=True,  # 1 point
        unilateral_leg_pain=True,  # 1 point
        unilateral_leg_edema=True,  # 1 point
        pain_on_palpation=True,  # 1 point
    )
    assert result.score == 10
    assert result.risk_level == GenevaRiskLevel.HIGH


def test_geneva_score_invalid_age():
    """Test Geneva score with invalid age."""
    with pytest.raises(ValueError, match="Age must be positive"):
        geneva_score(age=0)

    with pytest.raises(ValueError, match="Age must be positive"):
        geneva_score(age=-5)


def test_geneva_revised_minimal_case():
    """Test Revised Geneva score with minimal risk factors."""
    result = geneva_revised_score(age=30)

    assert result.score == 0
    assert result.risk_level == GenevaRiskLevel.LOW
    assert result.pe_probability == "8%"


def test_geneva_revised_age_scoring():
    """Test Revised Geneva score age-based scoring."""
    # Age < 65: 0 points
    result = geneva_revised_score(age=60)
    assert result.score == 0

    # Age >= 65: 1 point
    result = geneva_revised_score(age=70)
    assert result.score == 1


def test_geneva_revised_heart_rate_scoring():
    """Test Revised Geneva score heart rate scoring."""
    # HR < 75: 0 points
    result = geneva_revised_score(age=30, heart_rate=70)
    assert result.score == 0

    # HR 75-94: 3 points
    result = geneva_revised_score(age=30, heart_rate=85)
    assert result.score == 3

    # HR >= 95: 5 points
    result = geneva_revised_score(age=30, heart_rate=100)
    assert result.score == 5


def test_geneva_revised_all_factors():
    """Test Revised Geneva score with all risk factors."""
    result = geneva_revised_score(
        age=70,  # 1 point
        heart_rate=100,  # 5 points
        previous_pe_dvt=True,  # 3 points
        recent_surgery=True,  # 2 points
        hemoptysis=True,  # 2 points
        active_cancer=True,  # 2 points
        unilateral_leg_pain=True,  # 3 points
        unilateral_leg_edema=True,  # 4 points
        pain_on_palpation=True,  # 4 points
    )

    assert result.score == 26
    assert result.risk_level == GenevaRiskLevel.HIGH


def test_geneva_revised_risk_levels():
    """Test Revised Geneva score risk level classification."""
    # Low risk (0-3 points)
    result = geneva_revised_score(age=60, heart_rate=70)
    assert result.score == 0
    assert result.risk_level == GenevaRiskLevel.LOW

    # Intermediate risk (4-10 points)
    result = geneva_revised_score(age=70, heart_rate=85)  # 1 + 3 = 4 points
    assert result.score == 4
    assert result.risk_level == GenevaRiskLevel.INTERMEDIATE

    # High risk (>10 points)
    result = geneva_revised_score(
        age=70,  # 1 point
        heart_rate=100,  # 5 points
        previous_pe_dvt=True,  # 3 points
        recent_surgery=True,  # 2 points
    )
    assert result.score == 11
    assert result.risk_level == GenevaRiskLevel.HIGH


def test_geneva_revised_invalid_age():
    """Test Revised Geneva score with invalid age."""
    with pytest.raises(ValueError, match="Age must be positive"):
        geneva_revised_score(age=0)

    with pytest.raises(ValueError, match="Age must be positive"):
        geneva_revised_score(age=-5)


def test_geneva_revised_invalid_heart_rate():
    """Test Revised Geneva score with invalid heart rate."""
    with pytest.raises(ValueError, match="Heart rate must be between 1 and 300 bpm"):
        geneva_revised_score(age=50, heart_rate=0)

    with pytest.raises(ValueError, match="Heart rate must be between 1 and 300 bpm"):
        geneva_revised_score(age=50, heart_rate=350)


def test_geneva_revised_none_heart_rate():
    """Test Revised Geneva score with None heart rate."""
    result = geneva_revised_score(age=30, heart_rate=None)
    assert result.score == 0


def test_geneva_score_realistic_scenarios():
    """Test Geneva score with realistic clinical scenarios."""
    # Young healthy patient
    result = geneva_score(age=25)
    assert result.risk_level == GenevaRiskLevel.LOW

    # Elderly patient with some risk factors
    result = geneva_score(age=75, previous_pe_dvt=True, active_cancer=True)
    assert result.score == 3
    assert result.risk_level == GenevaRiskLevel.LOW

    # High-risk patient
    result = geneva_score(
        age=85,
        previous_pe_dvt=True,
        heart_rate_over_100=True,
        recent_surgery=True,
        active_cancer=True,
        unilateral_leg_pain=True,
    )
    assert result.score == 7
    assert result.risk_level == GenevaRiskLevel.INTERMEDIATE
