import pytest

from medimetry import Gender
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
    with pytest.raises(ValueError, match="Age must be positive"):
        chads_vasc_score(age=-1, gender=Gender.MALE)

    with pytest.raises(ValueError, match="Age must be positive"):
        chads_vasc_score(age=0, gender=Gender.MALE)


def test_chads_vasc_score_invalid_gender():
    """Test CHA2DS2-VASc score with invalid gender."""
    with pytest.raises(AssertionError):
        chads_vasc_score(age=50, gender="invalid")
