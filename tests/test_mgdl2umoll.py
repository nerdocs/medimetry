import pytest

from medimetry.converters import mgdl2umoll


def test_mgdl2umoll_normal_positive_value():
    """Test conversion of normal positive mg/dl value to umol/L."""
    result = mgdl2umoll(100.0)
    expected = 100.0 / 18.01528
    assert abs(result - expected) < 1e-10


def test_mgdl2umoll_zero():
    """Test that zero mg/dl converts to zero umol/L."""
    result = mgdl2umoll(0.0)
    assert result == 0.0


def test_mgdl2umoll_very_small_positive_values():
    """Test mgdl2umoll with very small positive values near zero."""
    result = mgdl2umoll(0.001)
    expected = 0.001 / 18.01528
    assert abs(result - expected) < 1e-10


def test_mgdl2umoll_very_large_positive_values():
    """Test that very large positive mg/dl values are handled without overflow."""
    large_mgdl = 1e10  # Very large positive value
    result = mgdl2umoll(large_mgdl)
    expected = large_mgdl / 18.01528
    assert result == expected
    assert isinstance(result, float)
    assert result != float("inf")


def test_mgdl2umoll_negative_values():
    """Test that negative mg/dl values are converted to negative umol/L."""
    result = mgdl2umoll(-100.0)
    expected = -100.0 / 18.01528
    assert result == expected
    assert result < 0


def test_mgdl2umoll_positive_infinity_raises_value_error():
    with pytest.raises(ValueError, match="Cannot convert infinity to mg/dl"):
        mgdl2umoll(float("inf"))


def test_mgdl2umoll_raises_value_error_for_negative_infinity():
    with pytest.raises(ValueError, match="Cannot convert negative infinity to mg/dl"):
        mgdl2umoll(float("-inf"))


def test_mgdl2umoll_floating_point_precision():
    """Test that mgdl2umoll handles floating point precision for typical glucose values."""
    # Test typical fasting glucose value
    result = mgdl2umoll(100.0)
    expected = 100.0 / 18.01528
    assert abs(result - expected) < 1e-10

    # Test typical post-meal glucose value with more decimal places
    result = mgdl2umoll(140.5)
    expected = 140.5 / 18.01528
    assert abs(result - expected) < 1e-10

    # Test very precise input value
    result = mgdl2umoll(99.99999)
    expected = 99.99999 / 18.01528
    assert abs(result - expected) < 1e-10


def test_mgdl2umoll_decimal_high_precision():
    """Test converting decimal mg/dl values with high precision."""
    # Test high precision decimal conversion
    result = mgdl2umoll(123.456789)
    expected = 123.456789 / 18.01528
    assert abs(result - expected) < 1e-10

    # Test very small decimal values
    result = mgdl2umoll(0.001)
    expected = 0.001 / 18.01528
    assert abs(result - expected) < 1e-12

    # Test large decimal values with precision
    result = mgdl2umoll(999.999999)
    expected = 999.999999 / 18.01528
    assert abs(result - expected) < 1e-10


def test_mgdl2umoll_handles_nan_input():
    """Test that mgdl2umoll handles NaN input appropriately."""
    import math

    from medimetry.converters import mgdl2umoll

    result = mgdl2umoll(float("nan"))
    assert math.isnan(result)
