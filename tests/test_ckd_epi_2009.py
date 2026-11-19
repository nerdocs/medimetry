"""CKD-EPI 2009 creatinine equation.

Expected values are computed from the sex- and creatinine-specific forms published in
Levey AS, et al. Ann Intern Med. 2009;150(9):604-612, Table 2 (coefficients 144 / 141,
166 / 163 for Black patients), which the single-formula implementation reproduces
within rounding.
"""

import pytest

from medimetry import EthnicalRace
from medimetry import Gender
from medimetry.renal import ckd_epi_2009

TOLERANCE = 0.5


@pytest.mark.parametrize(
    ("creatinine", "age", "gender", "expected"),
    [
        # female, Scr <= 0.7: 144 x (Scr/0.7)^-0.329 x 0.993^age
        (0.6, 50, Gender.FEMALE, 106.6),
        # female, Scr > 0.7: 144 x (Scr/0.7)^-1.209 x 0.993^age
        (1.2, 60, Gender.FEMALE, 49.2),
        # male, Scr <= 0.9: 141 x (Scr/0.9)^-0.411 x 0.993^age
        (0.8, 40, Gender.MALE, 111.7),
        # male, Scr > 0.9: 141 x (Scr/0.9)^-1.209 x 0.993^age
        (1.5, 70, Gender.MALE, 46.5),
    ],
)
def test_ckd_epi_2009_published_forms(creatinine, age, gender, expected):
    assert abs(ckd_epi_2009(creatinine=creatinine, age=age, gender=gender) - expected) < TOLERANCE


def test_ckd_epi_2009_black_coefficient():
    # male, Scr > 0.9, Black: 163 x (Scr/0.9)^-1.209 x 0.993^age
    result = ckd_epi_2009(creatinine=1.5, age=70, gender=Gender.MALE, race=EthnicalRace.AFRICAN_AMERICAN)
    assert abs(result - 53.8) < TOLERANCE


def test_ckd_epi_2009_rejects_diverse():
    with pytest.raises(ValueError):
        ckd_epi_2009(creatinine=1.0, age=50, gender=Gender.DIVERSE)
