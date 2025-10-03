import pytest

from medimetry.cardiac import qtc_correction
from medimetry.constants import QtcCorrectionType


def test_qtc_bazett_normal_values():
    """Test QTc calculation using Bazett formula with normal values."""
    # QT = 400ms, HR = 60 bpm (RR = 1.0s)
    # QTc = 400 / √1.0 = 400ms
    result = qtc_correction(400, 60, QtcCorrectionType.BAZETT)
    assert result == 400.0


def test_qtc_bazett_fast_heart_rate():
    """Test QTc calculation using Bazett formula with fast heart rate."""
    # QT = 350ms, HR = 100 bpm (RR = 0.6s)
    # QTc = 350 / √0.6 ≈ 350 / 0.7746 ≈ 451.8ms
    result = qtc_correction(350, 100, QtcCorrectionType.BAZETT)
    assert result == 451.8


def test_qtc_fridericia_normal_values():
    """Test QTc calculation using Fridericia formula."""
    # QT = 400ms, HR = 60 bpm (RR = 1.0s)
    # QTc = 400 / ∛1.0 = 400ms
    result = qtc_correction(400, 60, QtcCorrectionType.FRIDERICIA)
    assert result == 400.0


def test_qtc_framingham_normal_values():
    """Test QTc calculation using Framingham formula."""
    # QT = 400ms, HR = 60 bpm (RR = 1.0s)
    # QTc = 400 + 154 x (1 - 1.0) = 400ms
    result = qtc_correction(400, 60, QtcCorrectionType.FRAMINGHAM)
    assert result == 400.0


def test_qtc_hodges_normal_values():
    """Test QTc calculation using Hodges formula."""
    # QT = 400ms, HR = 60 bpm
    # QTc = 400 + 1.75 x (60 - 60) = 400ms
    result = qtc_correction(400, 60, QtcCorrectionType.HODGES)
    assert result == 400.0


def test_qtc_hodges_fast_heart_rate():
    """Test QTc calculation using Hodges formula with fast heart rate."""
    # QT = 350ms, HR = 100 bpm
    # QTc = 350 + 1.75 x (100 - 60) = 350 + 70 = 420ms
    result = qtc_correction(350, 100, QtcCorrectionType.HODGES)
    assert result == 420.0


def test_qtc_default_formula():
    """Test that Bazett is the default formula."""
    result1 = qtc_correction(400, 60)
    result2 = qtc_correction(400, 60, QtcCorrectionType.BAZETT)
    assert result1 == result2


def test_qtc_negative_qt_interval():
    """Test that ValueError is raised for negative QT interval."""
    with pytest.raises(ValueError, match="QT interval must be positive"):
        qtc_correction(-400, 60)


def test_qtc_zero_qt_interval():
    """Test that ValueError is raised for zero QT interval."""
    with pytest.raises(ValueError, match="QT interval must be positive"):
        qtc_correction(0, 60)


def test_qtc_negative_heart_rate():
    """Test that ValueError is raised for negative heart rate."""
    with pytest.raises(ValueError, match="Heart rate must be positive"):
        qtc_correction(400, -60)


def test_qtc_zero_heart_rate():
    """Test that ValueError is raised for zero heart rate."""
    with pytest.raises(ValueError, match="Heart rate must be positive"):
        qtc_correction(400, 0)


def test_qtc_excessive_heart_rate():
    """Test that ValueError is raised for unrealistic heart rate."""
    with pytest.raises(ValueError, match="Heart rate must be ≤ 300 bpm"):
        qtc_correction(400, 350)


def test_qtc_unsupported_formula():
    """Test that ValueError is raised for unsupported formula."""
    with pytest.raises(ValueError, match="Unsupported formula: invalid"):
        qtc_correction(400, 60, "invalid")


def test_qtc_rounding():
    """Test that QTc is properly rounded to 1 decimal place."""
    # Use values that would result in more decimal places
    result = qtc_correction(387.456, 73, QtcCorrectionType.BAZETT)
    # Should be rounded to 1 decimal place
    decimal_str = str(result).split(".")
    if len(decimal_str) > 1:
        assert len(decimal_str[1]) <= 1


def test_qtc_slow_heart_rate():
    """Test QTc calculation with slow heart rate."""
    # QT = 450ms, HR = 45 bpm (RR = 1.333s)
    # QTc = 450 / √1.333 ≈ 450 / 1.155 ≈ 389.7ms
    result = qtc_correction(450, 45, QtcCorrectionType.BAZETT)
    assert result == 389.7


def test_qtc_all_formulas_different_results():
    """Test that different formulas give different results for non-normal HR."""
    qt = 380
    hr = 90

    bazett = qtc_correction(qt, hr, QtcCorrectionType.BAZETT)
    fridericia = qtc_correction(qt, hr, QtcCorrectionType.FRIDERICIA)
    framingham = qtc_correction(qt, hr, QtcCorrectionType.FRAMINGHAM)
    hodges = qtc_correction(qt, hr, QtcCorrectionType.HODGES)

    # All should be different for HR != 60
    results = [bazett, fridericia, framingham, hodges]
    assert len(set(results)) == 4  # All unique values
