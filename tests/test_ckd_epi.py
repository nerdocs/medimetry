import pytest

from medimetry import Gender
from medimetry.renal import ckd_epi


def assert_in_range(result, expected):
    """Helper for asserting that a result is within a certain range of 0.1."""
    assert abs(result - expected) < 0.1


def test_ckd_epi_male_normal_creatinine():
    """Test CKD-EPI formula for male patient with normal creatinine levels."""
    # 50-year-old male, creatinine 1.0 mg/dl
    result = ckd_epi(creatinine=1.0, age=50, gender=Gender.MALE)
    expected = 91.6
    assert_in_range(result, expected)


def test_ckd_epi_male_elevated_creatinine():
    result = ckd_epi(creatinine=2.0, age=50, gender=Gender.MALE)
    expected = 40.0
    assert_in_range(result, expected)


def test_ckd_epi_female_normal_creatinine():
    """Test CKD-EPI formula for female patient with normal creatinine levels."""
    # 50-year-old female, creatinine 0.8 mg/dl
    result = ckd_epi(creatinine=0.8, age=50, gender=Gender.FEMALE)
    expected = 89.7
    assert_in_range(result, expected)


def test_ckd_epi_female_elevated_creatinine():
    """Test CKD-EPI formula for female patient with elevated creatinine levels."""
    # 60-year-old female, creatinine 2.5 mg/dl
    result = ckd_epi(creatinine=2.5, age=60, gender=Gender.FEMALE)
    expected = 21.4
    assert_in_range(result, expected)


def test_ckd_epi_male_with_cystatin_c():
    """Test CKD-EPI formula for male patient with cystatin C."""
    # 60-year-old male, creatinine 1.2 mg/dl, cystatin C 1.0 mg/dl
    result = ckd_epi(creatinine=1.2, age=60, gender=Gender.MALE, cystatin_c=1.0)
    expected = 76.8
    assert_in_range(result, expected)


def test_ckd_epi_female_with_cystatin_c():
    """Test CKD-EPI formula for female patient with cystatin C."""
    # 50-year-old female, creatinine 0.9 mg/dl, cystatin C 1.1 mg/dl
    result = ckd_epi(creatinine=0.9, age=50, gender=Gender.FEMALE, cystatin_c=1.1)
    expected = 72.8
    assert_in_range(result, expected)


def test_ckd_epi_zero_creatinine():
    """Test that AssertionError is raised for zero creatinine."""
    with pytest.raises(AssertionError, match="Creatinine must be positive"):
        ckd_epi(creatinine=0.0, age=50, gender=Gender.MALE)


def test_ckd_epi_negative_creatinine():
    """Test that AssertionError is raised for negative creatinine."""
    with pytest.raises(AssertionError, match="Creatinine must be positive"):
        ckd_epi(creatinine=-0.5, age=50, gender=Gender.MALE)


def test_ckd_epi_zero_age():
    """Test that AssertionError is raised for zero age."""
    with pytest.raises(AssertionError, match="Age must be positive"):
        ckd_epi(creatinine=1.0, age=0, gender=Gender.MALE)


def test_ckd_epi_negative_age():
    """Test that AssertionError is raised for negative age."""
    with pytest.raises(AssertionError, match="Age must be positive"):
        ckd_epi(creatinine=1.0, age=-5, gender=Gender.MALE)


def test_ckd_epi_invalid_gender():
    """Test that AssertionError is raised for invalid gender."""
    with pytest.raises(TypeError, match="Gender must be of type 'Gender'"):
        ckd_epi(creatinine=1.0, age=50, gender="invalid")


def test_ckd_epi_zero_cystatin_c():
    """Test that AssertionError is raised for zero cystatin C."""
    with pytest.raises(AssertionError, match="Cystatin C must be positive, if given"):
        ckd_epi(creatinine=1.0, age=50, gender=Gender.MALE, cystatin_c=0.0)


def test_ckd_epi_negative_cystatin_c():
    """Test that AssertionError is raised for negative cystatin C."""
    with pytest.raises(AssertionError, match="Cystatin C must be positive, if given"):
        ckd_epi(creatinine=1.0, age=50, gender=Gender.MALE, cystatin_c=-0.5)


def test_ckd_epi_very_low_creatinine():
    """Test CKD-EPI formula with very low creatinine values below kappa threshold."""
    # Female with very low creatinine (0.5 mg/dl, below kappa=0.7)
    result = ckd_epi(creatinine=0.5, age=30, gender=Gender.FEMALE)
    expected = 129.3
    assert_in_range(result, expected)

    # Male with very low creatinine (0.6 mg/dl, below kappa=0.9)
    result = ckd_epi(creatinine=0.6, age=30, gender=Gender.MALE)
    expected = 133.1
    assert_in_range(result, expected)


def test_ckd_epi_very_high_creatinine():
    """Test CKD-EPI formula with very high creatinine values above kappa threshold."""
    # Female with very high creatinine (2.5 mg/dl, above kappa=0.7)
    result = ckd_epi(creatinine=6.0, age=80, gender=Gender.FEMALE)
    expected = 6.7
    assert_in_range(result, expected)

    # Male with very high creatinine (3.0 mg/dl, above kappa=0.9)
    result = ckd_epi(creatinine=6.0, age=80, gender=Gender.MALE)
    expected = 8.8
    assert_in_range(result, expected)


def test_ckd_epi_elderly_patient():
    """Test CKD-EPI formula for elderly patient over 80 years."""
    # 85-year-old female, creatinine 1.2 mg/dl
    result = ckd_epi(creatinine=1.2, age=85, gender=Gender.FEMALE)
    expected = 44.3
    assert_in_range(result, expected)
