import pytest

from medimetry.cardiovasc import mean_arterial_pressure


def test_mean_arterial_pressure_normal_values():
    """Test MAP calculation for normal blood pressure values (120/80)."""
    result = mean_arterial_pressure(120, 80)
    expected = round((2 * 80 + 120) / 3, 1)  # (160 + 120) / 3 = 93.3
    assert result == expected
    assert result == 93.3


def test_mean_arterial_pressure_equal_values():
    """Test MAP calculation when systolic and diastolic pressures are equal."""
    with pytest.raises(
        ValueError,
        match="Diastolic pressure must be greater than systolic pressure",
    ):
        mean_arterial_pressure(100, 100)


def test_mean_arterial_pressure_minimum_valid_values():
    """Test MAP calculation when both systolic and diastolic are zero."""
    with pytest.raises(ValueError, match="Diastolic pressure must be non-negative"):
        mean_arterial_pressure(120, 0)
    with pytest.raises(ValueError, match="Systolic pressure must be non-negative"):
        mean_arterial_pressure(0, 120)


def test_mean_arterial_pressure_negative_systolic():
    """Test MAP calculation raises assertion error when systolic pressure is negative."""
    with pytest.raises(ValueError, match="Systolic pressure must be non-negative"):
        mean_arterial_pressure(-10, 80)


def test_mean_arterial_pressure_negative_diastolic():
    """Test MAP calculation raises assertion error when diastolic pressure is negative."""
    with pytest.raises(ValueError, match="Diastolic pressure must be non-negative"):
        mean_arterial_pressure(120, -10)


def test_mean_arterial_pressure_diastolic_exceeds_systolic():
    """Test MAP calculation raises assertion error when diastolic pressure exceeds systolic pressure."""
    with pytest.raises(ValueError):
        mean_arterial_pressure(119, 120)


def test_mean_arterial_pressure_rounding():
    """Test MAP calculation rounds result to one decimal place for values that require rounding."""
    result = mean_arterial_pressure(121, 81)
    expected = round((2 * 81 + 121) / 3, 1)  # (162 + 121) / 3 = 94.333... -> 94.3
    assert result == expected
    assert result == 94.3


def test_mean_arterial_pressure_high_blood_pressure():
    """Test MAP calculation for high blood pressure values (180/110)."""
    result = mean_arterial_pressure(180, 110)
    expected = round((2 * 110 + 180) / 3, 1)  # (220 + 180) / 3 = 133.3
    assert result == expected
    assert result == 133.3


def test_mean_arterial_pressure_large_valid_values():
    """Test MAP calculation for large but physiologically valid blood pressure values."""
    result = mean_arterial_pressure(200, 120)
    expected = round((2 * 120 + 200) / 3, 1)  # (240 + 200) / 3 = 146.7
    assert result == expected
    assert result == 146.7
