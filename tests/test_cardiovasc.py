import pytest

from medimetry import Gender
from medimetry.cardiovasc import calcium_correction
from medimetry.cardiovasc import chads_vasc_score


def test_chads_vasc_score_minimum():
    """Test CHA2DS2-VASc score with minimum risk factors."""
    # Young male with no risk factors
    score = chads_vasc_score(age=30, gender=Gender.MALE)
    assert score == 0


def test_chads_vasc_score_female_bonus():
    """Test CHA2DS2-VASc score with female gender bonus."""
    # Young female with no other risk factors gets 1 point
    score = chads_vasc_score(age=30, gender=Gender.FEMALE)
    assert score == 1


def test_chads_vasc_score_age_65_74():
    """Test CHA2DS2-VASc score for age 65-74 (1 point)."""
    score = chads_vasc_score(age=70, gender=Gender.MALE)
    assert score == 1


def test_chads_vasc_score_age_75_plus():
    """Test CHA2DS2-VASc score for age 75+ (2 points)."""
    score = chads_vasc_score(age=80, gender=Gender.MALE)
    assert score == 2


def test_chads_vasc_score_all_risk_factors():
    """Test CHA2DS2-VASc score with all risk factors."""
    score = chads_vasc_score(
        age=80,
        gender=Gender.FEMALE,
        chf=True,
        hypertension=True,
        stroke_vascular_history=True,
        diabetes=True,
        vascular_disease=True,
    )
    # Age 75+ (2) + Female (1) + CHF (1) + HTN (1) + Stroke (2) + DM (1) + Vasc (1) = 9
    assert score == 9


def test_chads_vasc_score_stroke_history_double_points():
    """Test that stroke/vascular history gives 2 points."""
    score = chads_vasc_score(age=30, gender=Gender.MALE, stroke_vascular_history=True)
    assert score == 2


def test_chads_vasc_score_invalid_age():
    """Test CHA2DS2-VASc score with invalid age."""
    with pytest.raises(ValueError, match="Age must be non-negative"):
        chads_vasc_score(age=-1, gender=Gender.MALE)

    with pytest.raises(ValueError, match="Age must be non-negative"):
        chads_vasc_score(age=0, gender=Gender.MALE)


def test_chads_vasc_score_invalid_gender():
    """Test CHA2DS2-VASc score with invalid gender."""
    with pytest.raises(AssertionError):
        chads_vasc_score(age=50, gender="invalid")


def test_calcium_correction_normal_albumin():
    """Test calcium correction with normal albumin."""
    # Normal albumin (4.0 g/dL), no correction needed
    result = calcium_correction(total_calcium=10.0, albumin=4.0)
    assert result == 10.0


def test_calcium_correction_low_albumin():
    """Test calcium correction with low albumin."""
    # Low albumin requires upward correction
    result = calcium_correction(total_calcium=8.5, albumin=3.0)
    # Corrected = 8.5 + 0.8 * (4.0 - 3.0) = 8.5 + 0.8 = 9.3
    assert result == 9.3


def test_calcium_correction_high_albumin():
    """Test calcium correction with high albumin."""
    # High albumin requires downward correction
    result = calcium_correction(total_calcium=10.5, albumin=5.0)
    # Corrected = 10.5 + 0.8 * (4.0 - 5.0) = 10.5 - 0.8 = 9.7
    assert result == 9.7


def test_calcium_correction_extreme_values():
    """Test calcium correction with extreme but valid values."""
    # Very low albumin
    result = calcium_correction(total_calcium=7.0, albumin=2.0)
    # Corrected = 7.0 + 0.8 * (4.0 - 2.0) = 7.0 + 1.6 = 8.6
    assert result == 8.6

    # Very high albumin
    result = calcium_correction(total_calcium=12.0, albumin=6.0)
    # Corrected = 12.0 + 0.8 * (4.0 - 6.0) = 12.0 - 1.6 = 10.4
    assert result == 10.4


def test_calcium_correction_precision():
    """Test calcium correction precision (rounded to 2 decimal places)."""
    result = calcium_correction(total_calcium=8.123, albumin=3.456)
    # Should be rounded to 2 decimal places
    assert len(str(result).split(".")[-1]) <= 2


def test_calcium_correction_negative_values():
    """Test calcium correction with negative values."""
    with pytest.raises(ValueError, match="Total calcium must be non-negative"):
        calcium_correction(total_calcium=-1.0, albumin=4.0)

    with pytest.raises(ValueError, match="Albumin must be non-negative"):
        calcium_correction(total_calcium=10.0, albumin=-1.0)
