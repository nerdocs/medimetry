import pytest
from labunits.converters import to_si_unit


def test_to_si_unit_normal_positive_value():
    """Test conversion of normal positive mg/dl value to umol/L."""
    result = to_si_unit("108797-2", 100.0)  # Potassium
    expected = 100.0 / 1
    assert abs(result - expected) < 1e-10


def test_to_si_unit_zero():
    """Test that zero mg/dl converts to zero umol/L."""
    result = to_si_unit(0.0)
    assert result == 0.0


def test_to_si_unit_very_small_positive_values():
    """Test to_si_unit with very small positive values near zero."""
    result = to_si_unit(0.001)
    expected = 0.001 / 18.01528
    assert abs(result - expected) < 1e-10


def test_to_si_unit_very_large_positive_values():
    """Test that very large positive mg/dl values are handled without overflow."""
    large_mgdl = 1e10  # Very large positive value
    result = to_si_unit(large_mgdl)
    expected = large_mgdl / 18.01528
    assert result == expected
    assert isinstance(result, float)
    assert result != float("inf")


def test_to_si_unit_negative_values():
    """Test that negative mg/dl values are converted to negative umol/L."""
    result = to_si_unit(-100.0)
    expected = -100.0 / 18.01528
    assert result == expected
    assert result < 0


def test_to_si_unit_positive_infinity_raises_value_error():
    with pytest.raises(ValueError, match="Cannot convert infinity to mg/dl"):
        to_si_unit(float("inf"))


def test_to_si_unit_raises_value_error_for_negative_infinity():
    with pytest.raises(ValueError, match="Cannot convert negative infinity to mg/dl"):
        to_si_unit(float("-inf"))


def test_to_si_unit_floating_point_precision():
    """Test that to_si_unit handles floating point precision for typical glucose values."""
    # Test typical fasting glucose value
    result = to_si_unit(100.0)
    expected = 100.0 / 18.01528
    assert abs(result - expected) < 1e-10

    # Test typical post-meal glucose value with more decimal places
    result = to_si_unit(140.5)
    expected = 140.5 / 18.01528
    assert abs(result - expected) < 1e-10

    # Test very precise input value
    result = to_si_unit(99.99999)
    expected = 99.99999 / 18.01528
    assert abs(result - expected) < 1e-10


def test_to_si_unit_decimal_high_precision():
    """Test converting decimal mg/dl values with high precision."""
    # Test high precision decimal conversion
    result = to_si_unit(123.456789)
    expected = 123.456789 / 18.01528
    assert abs(result - expected) < 1e-10

    # Test very small decimal values
    result = to_si_unit(0.001)
    expected = 0.001 / 18.01528
    assert abs(result - expected) < 1e-12

    # Test large decimal values with precision
    result = to_si_unit(999.999999)
    expected = 999.999999 / 18.01528
    assert abs(result - expected) < 1e-10


def test_to_si_unit_handles_nan_input():
    """Test that to_si_unit handles NaN input appropriately."""
    import math

    from medimetry.converters import to_si_unit

    result = to_si_unit(float("nan"))
    assert math.isnan(result)
