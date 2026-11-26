"""4-variable Kidney Failure Risk Equation (Tangri 2016, eAppendix 2).

risk = 1 - S0^exp(L), L = -0.2201 x (age/10 - 7.036) + 0.2467 x (male - 0.5642) - 0.5567 x (eGFR/5 - 7.222)
+ 0.4510 x (ln(ACR) - 5.137); S0 = 0.9750 / 0.9240 (North America, 2 / 5 years), 0.9832 / 0.9365 (elsewhere).

The expected percentages were calculated by hand (bc) from the equation as written above, not with the library.
"""

import math

import pytest

from medimetry import Gender
from medimetry import KfreRegion
from medimetry.formulas import formula
from medimetry.renal import kfre_2_year
from medimetry.renal import kfre_5_year

NA = KfreRegion.NORTH_AMERICA
NON_NA = KfreRegion.NON_NORTH_AMERICA


@pytest.mark.parametrize(
    ("function", "region", "expected"),
    [
        (kfre_2_year, NON_NA, 5.2683),
        (kfre_5_year, NON_NA, 18.9067),
        (kfre_2_year, NA, 7.7691),
        (kfre_5_year, NA, 22.3139),
    ],
)
def test_kfre_man_65_egfr_30_acr_300(function, region, expected):
    assert function(egfr=30, acr=300, age=65, gender=Gender.MALE, region=region) == pytest.approx(expected, abs=0.0001)


@pytest.mark.parametrize(("function", "expected"), [(kfre_2_year, 67.5062), (kfre_5_year, 98.7130)])
def test_kfre_woman_40_egfr_12_acr_1500(function, expected):
    assert function(egfr=12, acr=1500, age=40, gender=Gender.FEMALE, region=NON_NA) == pytest.approx(expected, abs=0.0001)


@pytest.mark.parametrize(
    ("function", "region", "survival"),
    [(kfre_2_year, NA, 0.9750), (kfre_2_year, NON_NA, 0.9832), (kfre_5_year, NA, 0.9240), (kfre_5_year, NON_NA, 0.9365)],
)
def test_kfre_at_the_centering_values_is_one_minus_baseline_survival(function, region, survival):
    """With every centred term at 0 only the sex term remains: risk = 1 - S0^exp(-0.2467 x 0.5642) for a woman."""
    risk = function(egfr=5 * 7.222, acr=math.exp(5.137), age=70.36, gender=Gender.FEMALE, region=region)
    assert risk == pytest.approx(100 * (1 - survival ** math.exp(-0.2467 * 0.5642)))


def test_kfre_sex_coefficient():
    """Men and women differ by exp(0.2467) in the hazard."""
    arguments = {"egfr": 25, "acr": 100, "age": 70, "region": NON_NA}
    hazard_male = math.log(1 - kfre_5_year(gender=Gender.MALE, **arguments) / 100)
    hazard_female = math.log(1 - kfre_5_year(gender=Gender.FEMALE, **arguments) / 100)
    assert hazard_male / hazard_female == pytest.approx(math.exp(0.2467))


def test_kfre_rounded():
    assert kfre_2_year(egfr=30, acr=300, age=65, gender=Gender.MALE, region=NON_NA, rounded=True) == 5.27
    assert kfre_5_year(egfr=30, acr=300, age=65, gender=Gender.MALE, region=NA, rounded=True) == 22.31


@pytest.mark.parametrize("function", [kfre_2_year, kfre_5_year])
@pytest.mark.parametrize(
    "arguments",
    [
        {"egfr": 60},  # CKD stages 3-5 only
        {"egfr": 0},
        {"egfr": -5},
        {"acr": 0},  # ln(0)
        {"acr": -1},
        {"age": 17},
        {"age": 0},
        {"gender": Gender.DIVERSE},
    ],
)
def test_kfre_outside_the_domain(function, arguments):
    valid = {"egfr": 30, "acr": 300, "age": 65, "gender": Gender.MALE, "region": NON_NA}
    with pytest.raises(ValueError):
        function(**(valid | arguments))


@pytest.mark.parametrize("function", [kfre_2_year, kfre_5_year])
@pytest.mark.parametrize("arguments", [{"gender": "m"}, {"region": "non_north_america"}])
def test_kfre_wrong_types(function, arguments):
    valid = {"egfr": 30, "acr": 300, "age": 65, "gender": Gender.MALE, "region": NON_NA}
    with pytest.raises(TypeError):
        function(**(valid | arguments))


def test_kfre_region_is_required():
    with pytest.raises(TypeError):
        kfre_2_year(egfr=30, acr=300, age=65, gender=Gender.MALE)


def test_kfre_registry():
    assert formula("kfre_2_year").loinc == "85624-5"
    assert formula("kfre_5_year").loinc == "85625-2"
    assert formula("kfre_5_year").unit == "%"
    assert formula("kfre_2_year").min_age == 18
