"""The formula registry and the shared rounding."""

import inspect

import pytest

from medimetry import Gender
from medimetry._formula import half_up
from medimetry.formulas import FORMULAS
from medimetry.formulas import formula


def test_ids_equal_function_names():
    for formula_id, info in FORMULAS.items():
        assert info.id == formula_id == info.function.__name__


def test_every_formula_is_unrounded_by_default_and_rounds_on_request():
    for info in FORMULAS.values():
        parameter = inspect.signature(info.function).parameters["rounded"]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, info.id
        assert parameter.default is False, info.id


def test_inputs_name_real_arguments():
    for info in FORMULAS.values():
        assert set(info.inputs) <= set(inspect.signature(info.function).parameters), info.id


def test_lookup():
    assert formula("ckd_epi_2021").loinc == "98979-8"
    assert formula("ckd_epi_2021").min_age == 18
    with pytest.raises(ValueError, match="Unknown formula"):
        formula("ckd_epi")


def test_rounded_uses_the_declared_digits():
    info = formula("ckd_epi_2021")
    raw = info.function(1.0, 50, Gender.MALE)
    assert info.function(1.0, 50, Gender.MALE, rounded=True) == half_up(raw, info.digits)


@pytest.mark.parametrize(
    ("value", "digits", "expected"),
    [
        (2.25, 1, 2.3),  # round() gives 2.2
        (0.125, 2, 0.13),  # round() gives 0.12
        (-4.75, 1, -4.8),
        (22.857, 1, 22.9),
        (7.0, 0, 7.0),
    ],
)
def test_half_up(value, digits, expected):
    assert half_up(value, digits) == expected
