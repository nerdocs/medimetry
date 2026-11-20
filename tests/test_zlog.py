"""zlog value (Hoffmann 2017).

Expected values are the deviations Cadamuro J, et al. Crit Rev Clin Lab Sci. 2021
(doi:10.1080/10408363.2020.1867051), Figure 6, plots for its blood count — which
cites Hoffmann's formula — recomputed to two places.
"""

import pytest

from medimetry.laboratory import zlog


@pytest.mark.parametrize(
    ("value", "lower", "upper", "expected"),
    [
        (5.9, 4.5, 5.9, 1.96),  # on the upper limit
        (111, 135, 177, -4.79),  # hemoglobin
        (60.1, 80, 96, -8.11),  # MCV
        (18.8, 28, 33, -11.46),  # MCH, beyond the figure's -10 axis
        (6.93, 3.5, 9.8, 0.64),  # white blood cells
    ],
)
def test_zlog(value, lower, upper, expected):
    assert zlog(value, lower, upper) == pytest.approx(expected, abs=0.005)


def test_zlog_geometric_centre_is_zero():
    assert zlog(6, 4, 9) == pytest.approx(0)


def test_zlog_is_unit_independent():
    assert zlog(111, 135, 177) == pytest.approx(zlog(11.1, 13.5, 17.7))


@pytest.mark.parametrize(
    ("value", "lower", "upper"),
    [
        (0, 1, 2),  # ln 0
        (-1, 1, 2),
        (1, 0, 5),  # one-sided interval written with 0 as lower limit
        (1, 5, 5),
        (1, 6, 5),
    ],
)
def test_zlog_rejects_invalid_input(value, lower, upper):
    with pytest.raises(ValueError):
        zlog(value, lower, upper)
