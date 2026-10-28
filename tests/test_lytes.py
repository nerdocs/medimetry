import pytest

from medimetry.lytes import calcium_correction


def test_calcium_correction_albumin_exactly_four():
    """Test that corrected calcium equals total calcium when albumin is exactly 4.0 g/dl."""

    # When albumin is exactly 4.0, the correction factor should be 0
    # Corrected Ca = Total Ca - 4.0 + 4.0 = Total Ca
    total_calcium = 9.5
    albumin = 4.0

    result = calcium_correction(total_calcium, albumin)
    assert result == 9.5  # Should equal the original total calcium value


def test_calcium_correction_albumin_below_four():
    """Test that corrected calcium is higher than total calcium when albumin is below 4.0 g/dl (hypoalbuminemia)."""

    # When albumin is below 4.0, the correction factor should be positive
    # Corrected Ca = Total Ca - 3.0 + 4.0 = Total Ca + 1.0
    total_calcium = 8.5
    albumin = 3.0

    result = calcium_correction(total_calcium, albumin)
    expected = 9.5  # 8.5 + 1.0
    assert result == expected
    assert result > total_calcium  # Corrected calcium should be higher than total calcium


def test_calcium_correction_albumin_above_four():
    """Test that corrected calcium is lower than total calcium when albumin is above 4.0 g/dl (hyperalbuminemia)."""

    # When albumin is above 4.0, the correction factor should be negative
    # Corrected Ca = Total Ca - 5.0 + 4.0 = Total Ca - 1.0
    total_calcium = 10.2
    albumin = 5.0

    result = calcium_correction(total_calcium, albumin)
    expected = 9.2  # 10.2 - 1.0
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
    # Corrected Ca = 0 - 0 + 4.0 = 4.0
    total_calcium = 0.0
    albumin = 0.0

    result = calcium_correction(total_calcium, albumin)
    expected = 0.0 - 0.0 + 4.0
    assert result == 4.0
    assert result == expected


def test_calcium_correction_rounding_to_two_decimal_places():
    """Test that corrected calcium is rounded to exactly 2 decimal places."""

    # Use values that would result in more than 2 decimal places without rounding
    # Corrected Ca = 9.3333 - 3.5 + 4.0 = 9.8333
    total_calcium = 9.3333
    albumin = 3.5

    result = calcium_correction(total_calcium, albumin)
    expected = 9.83  # Should be rounded to 2 decimal places
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
    expected = 0.001 - 0.001 + 4.0
    expected_rounded = round(expected, 2)  # 4.00
    assert result == expected_rounded
    assert result == 4.0


def test_calcium_correction_very_large_values():
    """Test that corrected calcium calculation handles very large values for both total calcium and albumin correctly."""

    # TODO: should we add constraints for useful lower/upper boundaries? This test is
    #  factically correct, but in medicine completely useless

    # Use very large values to test numerical stability
    total_calcium = 1000000.0
    albumin = 500000.0

    result = calcium_correction(total_calcium, albumin)
    expected = 1000000.0 - 500000.0 + 4.0
    expected_rounded = round(expected, 2)  # 500004.00
    assert result == expected_rounded
    assert result == 500004.0
