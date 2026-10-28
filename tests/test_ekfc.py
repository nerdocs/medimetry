import math

import pytest

from medimetry import Gender
from medimetry.renal import ekfc


def test_ekfc_male_adult_above_q():
    """SCr/Q >= 1 with age factor: 107.3 x (88.4/80)^-1.132 x 0.990^10."""
    expected = 107.3 * (88.4 / 80) ** -1.132 * 0.990**10
    assert ekfc(creatinine=1.0, age=50, gender=Gender.MALE) == pytest.approx(expected)
    assert ekfc(creatinine=1.0, age=50, gender=Gender.MALE) == pytest.approx(86.7, abs=0.1)


def test_ekfc_female_adult_below_q_no_age_factor():
    """SCr/Q < 1 at age <= 40: no age factor."""
    expected = 107.3 * (0.6 * 88.4 / 62) ** -0.322
    assert ekfc(creatinine=0.6, age=30, gender=Gender.FEMALE) == pytest.approx(expected)


def test_ekfc_median_creatinine_gives_107_3():
    """A creatinine equal to Q yields 107.3 up to 40 years."""
    assert ekfc(creatinine=80 / 88.4, age=35, gender=Gender.MALE) == pytest.approx(107.3)
    assert ekfc(creatinine=62 / 88.4, age=40, gender=Gender.FEMALE) == pytest.approx(107.3)


def test_ekfc_child_q_polynomial():
    """Ages 2-25 use the published ln(Q) polynomial (µmol/l)."""
    age = 8
    q = math.exp(3.200 + 0.259 * age - 0.543 * math.log(age) - 0.00763 * age**2 + 0.0000790 * age**3)
    expected = 107.3 * (0.4 * 88.4 / q) ** -0.322
    assert ekfc(creatinine=0.4, age=age, gender=Gender.MALE) == pytest.approx(expected)


def test_ekfc_child_female_q_polynomial():
    age = 12.5
    q = math.exp(3.080 + 0.177 * age - 0.223 * math.log(age) - 0.00596 * age**2 + 0.0000686 * age**3)
    expected = 107.3 * (1.0 * 88.4 / q) ** -1.132
    assert ekfc(creatinine=1.0, age=age, gender=Gender.FEMALE) == pytest.approx(expected)


def test_ekfc_with_cystatin_c_is_mean():
    """Cystatin C: Q = 0.83 + 0.005 x (age - 50) from 50 years; result is the mean of both."""
    egfr_cr = ekfc(creatinine=1.2, age=60, gender=Gender.MALE)
    egfr_cys = 107.3 * (1.0 / 0.88) ** -1.132 * 0.990**20
    result = ekfc(creatinine=1.2, age=60, gender=Gender.MALE, cystatin_c=1.0)
    assert result == pytest.approx((egfr_cr + egfr_cys) / 2)


def test_ekfc_cystatin_c_q_below_50():
    egfr_cr = ekfc(creatinine=0.7, age=30, gender=Gender.FEMALE)
    egfr_cys = 107.3 * (0.7 / 0.83) ** -0.322
    result = ekfc(creatinine=0.7, age=30, gender=Gender.FEMALE, cystatin_c=0.7)
    assert result == pytest.approx((egfr_cr + egfr_cys) / 2)


def test_ekfc_under_2_years():
    with pytest.raises(ValueError):
        ekfc(creatinine=0.3, age=1.5, gender=Gender.MALE)


def test_ekfc_zero_creatinine():
    with pytest.raises(AssertionError):
        ekfc(creatinine=0.0, age=50, gender=Gender.MALE)


def test_ekfc_zero_cystatin_c():
    with pytest.raises(AssertionError):
        ekfc(creatinine=1.0, age=50, gender=Gender.MALE, cystatin_c=0.0)


def test_ekfc_invalid_gender():
    with pytest.raises(TypeError):
        ekfc(creatinine=1.0, age=50, gender="invalid")
