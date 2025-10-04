import pytest

from medimetry.converters import umoll2mgdl


def test_umoll2mgdl_zero():
    """Test that zero umol/L converts to zero mg/dl."""

    result = umoll2mgdl(0.0)
    assert result == 0.0


def test_umoll2mgdl_zero_value():
    """Test conversion with zero umol/L value."""
    result = umoll2mgdl(0.0)
    assert result == 0.0


def test_umoll2mgdl_positive_integer():
    """Test that positive integer umol/L values convert to correct mg/dl."""

    result = umoll2mgdl(100)
    assert result == 1801.528


def test_umoll2mgdl_positive_decimal():
    """Test that positive decimal umol/L values convert to correct mg/dl."""

    result = umoll2mgdl(88.4)
    assert result == 1592.5507520000001


def test_umoll2mgdl_negative_value():
    """Test that negative umol/L values convert to negative mg/dl."""

    result = umoll2mgdl(-50.0)
    assert result == -900.764


def test_umoll2mgdl_very_large_value():
    """Test that very large umol/L values convert without overflow."""

    result = umoll2mgdl(1000000.0)
    assert result == 18015280.0


def test_umoll2mgdl_very_small_positive():
    """Test that very small positive umol/L values near zero convert correctly."""

    result = umoll2mgdl(0.001)
    assert result == 0.01801528


def test_umoll2mgdl_clinical_glucose_range():
    """Test that typical clinical glucose range values maintain precision."""

    # Normal fasting glucose: ~5.6 mmol/L
    result = umoll2mgdl(5.6)
    assert abs(result - 100.88557) < 0.00001

    # Diabetes threshold: ~7.0 mmol/L
    result = umoll2mgdl(7.0)
    assert abs(result - 126.10696) < 0.00001

    # High glucose: ~15.0 mmol/L
    result = umoll2mgdl(15.0)
    assert abs(result - 270.2292) < 0.0001


def test_umoll2mgdl_infinity():
    """Test that infinity umol/L values convert to infinity mg/dl."""

    with pytest.raises(ValueError, match="Cannot convert infinity to mg/dl"):
        umoll2mgdl(float("inf"))


def test_umoll2mgdl_negative_infinity():
    """Test that negative infinity umol/L values convert to negative infinity mg/dl."""

    with pytest.raises(ValueError, match="Cannot convert negative infinity to mg/dl"):
        umoll2mgdl(float("-inf"))


def test_umoll2mgdl_fractional_values():
    """Test that fractional umol/L values convert accurately using the conversion factor."""

    result = umoll2mgdl(2.5)
    expected = 2.5 * 18.01528
    assert abs(result - expected) < 0.000001
    assert abs(result - 45.0382) < 0.0001
