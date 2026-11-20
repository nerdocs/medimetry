"""
CKD-EPI 2021 tests.

Source of the expected eGFR values: recomputed from the published equations, not taken from a published worked
example (Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749, doi:10.1056/NEJMoa2102953, which gives none):

- creatinine: 142 x min(Scr/k, 1)^a x max(Scr/k, 1)^-1.200 x 0.9938^age x 1.012 [female], k 0.7 / 0.9, a -0.241 / -0.302
- creatinine-cystatin C: 135 x min(Scr/k, 1)^a x max(Scr/k, 1)^-0.544 x min(Scys/0.8, 1)^-0.323
  x max(Scys/0.8, 1)^-0.778 x 0.9961^age x 0.963 [female], a -0.219 / -0.144

An independent recomputation (outside medimetry) agrees with every expected value within the 0.1 tolerance of
``assert_in_range``; several expected values are truncated rather than rounded to one decimal (e.g. 91.69 -> 91.6).
"""

import pytest

from medimetry import Gender
from medimetry.renal import ckd_epi
from medimetry.renal import ckd_epi_2021
from medimetry.renal import ckd_epi_2021_cystatin


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
    result = ckd_epi_2021_cystatin(creatinine=1.2, cystatin_c=1.0, age=60, gender=Gender.MALE)
    expected = 76.8
    assert_in_range(result, expected)


def test_ckd_epi_female_with_cystatin_c():
    """Test CKD-EPI formula for female patient with cystatin C."""
    # 50-year-old female, creatinine 0.9 mg/dl, cystatin C 1.1 mg/dl
    result = ckd_epi_2021_cystatin(creatinine=0.9, cystatin_c=1.1, age=50, gender=Gender.FEMALE)
    expected = 72.8
    assert_in_range(result, expected)


def test_ckd_epi_zero_creatinine():
    """Test that ValueError is raised for zero creatinine."""
    with pytest.raises(ValueError, match="Creatinine must be positive"):
        ckd_epi(creatinine=0.0, age=50, gender=Gender.MALE)


def test_ckd_epi_negative_creatinine():
    """Test that ValueError is raised for negative creatinine."""
    with pytest.raises(ValueError, match="Creatinine must be positive"):
        ckd_epi(creatinine=-0.5, age=50, gender=Gender.MALE)


@pytest.mark.parametrize("age", [-5, 0, 17.9])
def test_ckd_epi_below_adult_age(age):
    """The equation was derived in adults: below 18 years it raises."""
    with pytest.raises(ValueError, match="only defined from 18 years"):
        ckd_epi(creatinine=1.0, age=age, gender=Gender.MALE)


def test_ckd_epi_follows_the_newest_equation():
    assert ckd_epi(creatinine=1.0, age=50, gender=Gender.MALE) == ckd_epi_2021(creatinine=1.0, age=50, gender=Gender.MALE)


def test_ckd_epi_invalid_gender():
    """Test that TypeError is raised for invalid gender."""
    with pytest.raises(TypeError, match="Gender must be of type 'Gender'"):
        ckd_epi(creatinine=1.0, age=50, gender="invalid")


def test_ckd_epi_zero_cystatin_c():
    """Test that ValueError is raised for zero cystatin C."""
    with pytest.raises(ValueError, match="Cystatin C must be positive"):
        ckd_epi_2021_cystatin(creatinine=1.0, cystatin_c=0.0, age=50, gender=Gender.MALE)


def test_ckd_epi_negative_cystatin_c():
    """Test that ValueError is raised for negative cystatin C."""
    with pytest.raises(ValueError, match="Cystatin C must be positive"):
        ckd_epi_2021_cystatin(creatinine=1.0, cystatin_c=-0.5, age=50, gender=Gender.MALE)


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


def test_ckd_epi_diverse_gender():
    with pytest.raises(ValueError):
        ckd_epi(creatinine=1.0, age=50, gender=Gender.DIVERSE)
