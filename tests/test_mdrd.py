import pytest

from medimetry import EthnicalRace
from medimetry import Gender
from medimetry.renal import mdrd


def test_mdrd_male_normal_creatinine():
    """Test MDRD formula for male patient with normal creatinine levels."""
    # 50-year-old male, creatinine 1.0 mg/dl, other race
    result = mdrd(creatinine=1.0, age=50, gender=Gender.MALE, race=EthnicalRace.OTHER)
    expected = 175 * (1.0**-1.154) * (50**-0.203)  # ~79.7 mL/min/1.73m²
    assert abs(result - expected) < 0.1
    assert 75 < result < 85  # Should be in normal range


def test_mdrd_female_correction_factor():
    """Test MDRD formula applies 0.742 correction factor for female patients."""
    # Test with same parameters but different gender to verify correction factor
    male_result = mdrd(creatinine=1.0, age=50, gender=Gender.MALE, race=EthnicalRace.OTHER)
    female_result = mdrd(creatinine=1.0, age=50, gender=Gender.FEMALE, race=EthnicalRace.OTHER)

    # Female result should be male result * 0.742
    expected_female = male_result * 0.742
    assert abs(female_result - expected_female) < 0.001  # Allow for floating point precision
    assert female_result < male_result  # Female result should be lower


def test_mdrd_african_american_correction():
    """Test MDRD formula with African American race correction factor."""
    # 50-year-old African American male, creatinine 1.2 mg/dl
    result = mdrd(creatinine=1.2, age=50, gender=Gender.MALE, race=EthnicalRace.AFRICAN_AMERICAN)

    # Calculate expected value: 175 * (1.2)^-1.154 * (50)^-0.203 * 1.212
    base_calculation = 175 * (1.2**-1.154) * (50**-0.203)
    expected = base_calculation * 1.212

    assert abs(result - expected) < 0.01  # Allow small floating point differences
    assert result > base_calculation  # African American factor should increase result


def test_mdrd_african_american_female():
    """Test MDRD formula for African American female with both correction factors."""
    # 50-year-old African American female, creatinine 1.2 mg/dl
    result = mdrd(creatinine=1.2, age=50, gender=Gender.FEMALE, race=EthnicalRace.AFRICAN_AMERICAN)
    # Base: 175 * (1.2)^-1.154 * (50)^-0.203 = 175 * 0.8676 * 0.4472 = 67.88
    # Female factor: 67.88 * 0.742 = 50.37
    # African American factor: 50.37 * 1.212 = 61.05
    expected = 57.6
    assert abs(result - expected) < 0.1


def test_mdrd_zero_creatinine():
    """Test MDRD formula with zero creatinine."""
    with pytest.raises(AssertionError, match="Creatinine must be positive"):
        mdrd(creatinine=0.0, age=50, gender=Gender.MALE)


def test_mdrd_negative_creatinine():
    """Test MDRD formula with negative creatinine."""
    with pytest.raises(AssertionError, match="Creatinine must be positive"):
        mdrd(creatinine=-0.5, age=50, gender=Gender.MALE)


def test_mdrd_zero_age():
    """Test MDRD formula with zero age."""
    with pytest.raises(AssertionError, match="Age must be positive"):
        mdrd(creatinine=1.0, age=0, gender=Gender.MALE)


def test_mdrd_negative_age():
    """Test MDRD formula with negative age."""
    with pytest.raises(AssertionError, match="Age must be positive"):
        mdrd(creatinine=1.0, age=-5, gender=Gender.MALE)


def test_mdrd_elderly_over_100():
    """Test MDRD formula for elderly patients over 100 years."""
    # 105-year-old male, creatinine 1.2 mg/dl
    result = mdrd(creatinine=1.2, age=105, gender=Gender.MALE)
    # Manual calculation: 175 * (1.2)^-1.154 * (105)^-0.203
    # = 175 * 0.8551 * 0.3147 ≈ 47.1
    assert 55.1 < result < 55.2
    assert isinstance(result, float)
