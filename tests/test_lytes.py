import pytest

from medimetry.cardio import calcium_correction


def test_calcium_correction_albumin_exactly_four():
    """Test that corrected calcium equals total calcium when albumin is exactly 4.0 g/dL."""

    # When albumin is exactly 4.0, the correction factor should be 0
    # Corrected Ca = Total Ca + 0.8 x (4.0 - 4.0) = Total Ca + 0
    total_calcium = 9.5
    albumin = 4.0

    result = calcium_correction(total_calcium, albumin)
    assert result == 9.5  # Should equal the original total calcium value


def test_calcium_correction_albumin_below_four():
    """Test that corrected calcium is higher than total calcium when albumin is below 4.0 g/dL (hypoalbuminemia)."""

    # When albumin is below 4.0, the correction factor should be positive
    # Corrected Ca = Total Ca + 0.8 x (4.0 - 3.0) = Total Ca + 0.8
    total_calcium = 8.5
    albumin = 3.0

    result = calcium_correction(total_calcium, albumin)
    expected = 8.5 + 0.8 * (4.0 - 3.0)  # 8.5 + 0.8 = 9.3
    assert result == expected
    assert result > total_calcium  # Corrected calcium should be higher than total calcium


def test_calcium_correction_albumin_above_four():
    """Test that corrected calcium is lower than total calcium when albumin is above 4.0 g/dL (hyperalbuminemia)."""

    # When albumin is above 4.0, the correction factor should be negative
    # Corrected Ca = Total Ca + 0.8 x (4.0 - 5.0) = Total Ca - 0.8
    total_calcium = 10.2
    albumin = 5.0

    result = calcium_correction(total_calcium, albumin)
    expected = round(10.2 + 0.8 * (4.0 - 5.0), 1)  # 10.2 - 0.8 = 9.4
    assert result == expected
    assert result < total_calcium  # Corrected calcium should be lower than total calcium


def test_calcium_correction_negative_total_calcium():
    """Test that ValueError is raised when total calcium is negative."""

    with pytest.raises(ValueError, match="Total calcium must be non-negative"):
        calcium_correction(-1.5, 3.5)


def test_calcium_correction_negative_albumin():
    """Test that ValueError is raised when albumin is negative."""

    with pytest.raises(ValueError, match="Albumin must be non-negative"):
        calcium_correction(9.5, -2.0)


def test_calcium_correction_zero_values():
    """Test that corrected calcium calculation handles zero values for both total calcium and albumin correctly."""

    # When both total calcium and albumin are zero
    # Corrected Ca = 0 + 0.8 x (4.0 - 0) = 0 + 3.2 = 3.2
    total_calcium = 0.0
    albumin = 0.0

    result = calcium_correction(total_calcium, albumin)
    expected = 0.0 + 0.8 * (4.0 - 0.0)  # 0 + 3.2 = 3.2
    assert result == 3.2
    assert result == expected


def test_calcium_correction_rounding_to_two_decimal_places():
    """Test that corrected calcium is rounded to exactly 2 decimal places."""

    # Use values that would result in more than 2 decimal places without rounding
    # Corrected Ca = 9.333 + 0.8 x (4.0 - 3.333) = 9.333 + 0.8 x 0.667 = 9.333 + 0.5336 = 9.8666
    total_calcium = 9.333
    albumin = 3.333

    result = calcium_correction(total_calcium, albumin)
    expected = 9.87  # Should be rounded to 2 decimal places
    assert result == expected

    # Verify the result has exactly 2 decimal places
    decimal_str = str(result).split(".")
    if len(decimal_str) > 1:
        assert len(decimal_str[1]) <= 2


def test_calcium_correction_very_small_positive_values():
    """Test that corrected calcium calculation handles very small positive values for both total calcium and albumin correctly."""

    # Use very small positive values near zero
    total_calcium = 0.001
    albumin = 0.001

    result = calcium_correction(total_calcium, albumin)
    expected = 0.001 + 0.8 * (4.0 - 0.001)  # 0.001 + 0.8 * 3.999 = 0.001 + 3.1992 = 3.2002
    expected_rounded = round(expected, 2)  # 3.20
    assert result == expected_rounded
    assert result == 3.20


def test_calcium_correction_very_large_values():
    """Test that corrected calcium calculation handles very large values for both total calcium and albumin correctly."""

    # TODO: should we add constraints for useful lower/upper boundaries? This test is
    #  factically correct, but in medicine completely useless

    # Use very large values to test numerical stability
    total_calcium = 1000000.0
    albumin = 500000.0

    result = calcium_correction(total_calcium, albumin)
    expected = 1000000.0 + 0.8 * (4.0 - 500000.0)  # 1000000.0 + 0.8 * (-499996.0) = 1000000.0 - 399996.8 = 600003.2
    expected_rounded = round(expected, 2)  # 600003.20
    assert result == expected_rounded
    assert result == 600003.20
