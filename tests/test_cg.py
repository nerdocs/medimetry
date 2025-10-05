import pytest

from medimetry.constants import Gender
from medimetry.renal import cockcroft_gault


def test_cockcroft_gault_male_normal():
    """Test Cockcroft-Gault formula for normal male patient."""
    # 70-year-old male, 70kg, creatinine 1.0 mg/dl
    result = cockcroft_gault(age=70, weight=70, creatinine=1.0, gender=Gender.MALE)
    expected = round(((140 - 70) * 70) / (72 * 1.0))  # 68 mL/min
    assert result == expected
    assert result == 68


def test_cockcroft_gault_female_normal():
    """Test Cockcroft-Gault formula for normal female patient."""
    # 70-year-old female, 60kg, creatinine 1.0 mg/dl
    result = cockcroft_gault(age=70, weight=60, creatinine=1.0, gender=Gender.FEMALE)
    expected = round(((140 - 70) * 60) / (72 * 1.0) * 0.85)  # 49 mL/min
    assert result == expected
    assert result == 50


def test_cockcroft_gault_young_patient():
    """Test Cockcroft-Gault formula for young patient."""
    # 30-year-old male, 80kg, creatinine 0.8 mg/dl
    result = cockcroft_gault(age=30, weight=80, creatinine=0.8, gender=Gender.MALE)
    expected = round(((140 - 30) * 80) / (72 * 0.8))  # 153 mL/min
    assert result == expected
    assert result == 153


def test_cockcroft_gault_elderly_patient():
    """Test Cockcroft-Gault formula for elderly patient."""
    # 85-year-old female, 55kg, creatinine 1.5 mg/dl
    result = cockcroft_gault(age=85, weight=55, creatinine=1.5, gender=Gender.FEMALE)
    expected = round(((140 - 85) * 55) / (72 * 1.5) * 0.85)  # 25 mL/min
    assert result == expected
    assert result == 24


def test_cockcroft_gault_high_creatinine():
    """Test Cockcroft-Gault formula with high creatinine."""
    # 60-year-old male, 75kg, creatinine 3.0 mg/dl
    result = cockcroft_gault(age=60, weight=75, creatinine=3.0, gender=Gender.MALE)
    expected = round(((140 - 60) * 75) / (72 * 3.0))  # 28 mL/min
    assert result == expected
    assert result == 28


def test_cockcroft_gault_zero_weight():
    """Test Cockcroft-Gault formula with zero weight."""
    with pytest.raises(AssertionError, match="Weight must be positive"):
        cockcroft_gault(age=50, weight=0, creatinine=1.0, gender=Gender.MALE)


def test_cockcroft_gault_negative_weight():
    """Test Cockcroft-Gault formula with negative weight."""
    with pytest.raises(AssertionError, match="Weight must be positive"):
        cockcroft_gault(age=50, weight=-10, creatinine=1.0, gender=Gender.MALE)


def test_cockcroft_gault_excessive_weight():
    """Test Cockcroft-Gault formula with excessive weight."""
    with pytest.raises(AssertionError, match="Weight must be less than 400 kg"):
        cockcroft_gault(age=50, weight=450, creatinine=1.0, gender=Gender.MALE)


def test_cockcroft_gault_zero_age():
    """Test Cockcroft-Gault formula with zero age."""
    with pytest.raises(AssertionError, match="Age must be positive"):
        cockcroft_gault(age=0, weight=70, creatinine=1.0, gender=Gender.MALE)


def test_cockcroft_gault_negative_age():
    """Test Cockcroft-Gault formula with negative age."""
    with pytest.raises(AssertionError, match="Age must be positive"):
        cockcroft_gault(age=-5, weight=70, creatinine=1.0, gender=Gender.MALE)


def test_cockcroft_gault_negative_creatinine():
    """Test Cockcroft-Gault formula with negative creatinine."""
    with pytest.raises(AssertionError, match="Creatinine must not be negative"):
        cockcroft_gault(age=50, weight=70, creatinine=-0.5, gender=Gender.MALE)


def test_cockcroft_gault_zero_creatinine():
    """Test Cockcroft-Gault formula with zero creatinine."""
    # Zero creatinine should be allowed (though clinically unrealistic)
    with pytest.raises(ValueError, match="Creatinine must be non-zero"):
        cockcroft_gault(age=50, weight=70, creatinine=0.0, gender=Gender.MALE)
    # This would result in division by zero, so the function should handle this


def test_cockcroft_gault_invalid_gender():
    """Test Cockcroft-Gault formula with invalid gender."""
    with pytest.raises(AssertionError, match="gender must be a Gender instance"):
        cockcroft_gault(age=50, weight=70, creatinine=1.0, gender="invalid")
    with pytest.raises(AssertionError, match="gender must be a Gender instance"):
        cockcroft_gault(age=50, weight=70, creatinine=1.0, gender=2)


def test_cockcroft_gault_realistic_scenarios():
    """Test Cockcroft-Gault formula with realistic clinical scenarios."""
    # Healthy young adult male
    result = cockcroft_gault(age=25, weight=75, creatinine=0.9, gender=Gender.MALE)
    assert result > 100  # Should have good kidney function

    # Elderly female with mild kidney impairment
    result = cockcroft_gault(age=80, weight=60, creatinine=1.3, gender=Gender.FEMALE)
    assert 30 < result < 60  # Moderate kidney impairment

    # Middle-aged male with normal function
    result = cockcroft_gault(age=45, weight=80, creatinine=1.1, gender=Gender.MALE)
    assert 60 < result < 120  # Normal to mildly reduced


def test_cockcroft_gault_gender_difference():
    """Test that female patients have lower clearance than male patients."""
    male_result = cockcroft_gault(age=60, weight=70, creatinine=1.0, gender=Gender.MALE)
    female_result = cockcroft_gault(age=60, weight=70, creatinine=1.0, gender=Gender.FEMALE)

    # Female result should be 85% of male result
    expected_female = round(male_result * 0.85)
    assert female_result < male_result
    assert abs(female_result - expected_female) <= 1  # Allow for rounding differences


def test_cockcroft_gault_return_type():
    """Test that Cockcroft-Gault returns an integer."""
    result = cockcroft_gault(age=50, weight=70, creatinine=1.0, gender=Gender.MALE)
    assert isinstance(result, int)
