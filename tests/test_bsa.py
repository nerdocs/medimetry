import pytest

from medimetry.anthropometric import BSAFormula
from medimetry.anthropometric import bsa
from medimetry.anthropometric import bsa_all_formulas
from medimetry.anthropometric import bsa_boyd
from medimetry.anthropometric import bsa_dubois
from medimetry.anthropometric import bsa_from_cm
from medimetry.anthropometric import bsa_gehan_george
from medimetry.anthropometric import bsa_haycock
from medimetry.anthropometric import bsa_mosteller


def test_bsa_mosteller():
    """Test BSA calculation using Mosteller formula."""
    # Standard adult male (70kg, 175cm)
    result = bsa_mosteller(70, 1.75)
    assert result == 1.84

    # Standard adult female (60kg, 165cm)
    result = bsa_mosteller(60, 1.65)
    assert result == 1.66


def test_bsa_dubois():
    """Test BSA calculation using DuBois formula."""
    # Standard adult male (70kg, 175cm)
    result = bsa_dubois(70, 1.75)
    assert result == 1.85

    # Standard adult female (60kg, 165cm)
    result = bsa_dubois(60, 1.65)
    assert result == 1.66


def test_bsa_haycock():
    """Test BSA calculation using Haycock formula."""
    # Standard adult male (70kg, 175cm)
    result = bsa_haycock(70, 1.75)
    assert result == 1.85

    # Standard adult female (60kg, 165cm)
    result = bsa_haycock(60, 1.65)
    assert result == 1.66


def test_bsa_gehan_george():
    """Test BSA calculation using Gehan-George formula."""
    # Standard adult male (70kg, 175cm)
    result = bsa_gehan_george(70, 1.75)
    assert result == 1.85

    # Standard adult female (60kg, 165cm)
    result = bsa_gehan_george(60, 1.65)
    assert result == 1.67


def test_bsa_boyd():
    """Test BSA calculation using Boyd formula."""
    # Standard adult male (70kg, 175cm)
    result = bsa_boyd(70, 1.75)
    assert result == 1.85

    # Standard adult female (60kg, 165cm)
    result = bsa_boyd(60, 1.65)
    assert result == 1.67


def test_bsa_default_formula():
    """Test BSA calculation with default formula (Mosteller)."""
    result = bsa(70, 1.75)
    expected = bsa_mosteller(70, 1.75)
    assert result == expected


def test_bsa_with_specific_formula():
    """Test BSA calculation with specific formula."""
    result = bsa(70, 1.75, BSAFormula.DUBOIS)
    expected = bsa_dubois(70, 1.75)
    assert result == expected


def test_bsa_from_cm():
    """Test BSA calculation with height in centimeters."""
    result = bsa_from_cm(70, 175)
    expected = bsa(70, 1.75)
    assert result == expected


def test_bsa_all_formulas():
    """Test BSA calculation using all formulas."""
    results = bsa_all_formulas(70, 1.75)

    assert len(results) == 5
    assert "DuBois" in results
    assert "Mosteller" in results
    assert "Haycock" in results
    assert "Gehan-George" in results
    assert "Boyd" in results

    # Check that all values are reasonable (between 1.5 and 2.5 for normal adult)
    for formula_name, bsa_value in results.items():
        assert 1.5 <= bsa_value <= 2.5, f"{formula_name}: {bsa_value}"


def test_bsa_extreme_values():
    """Test BSA calculation with extreme but valid values."""
    # Very small person (child-like)
    result = bsa_mosteller(20, 1.20)
    assert result == 0.82

    # Very large person
    result = bsa_mosteller(120, 2.00)
    assert result == 2.58


def test_bsa_invalid_weight():
    """Test BSA calculation with invalid weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_mosteller(0, 1.75)

    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_mosteller(-10, 1.75)


def test_bsa_invalid_height():
    """Test BSA calculation with invalid height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_mosteller(70, 0)

    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_mosteller(70, -1.75)


def test_bsa_invalid_height_cm():
    """Test BSA calculation with invalid height in centimeters."""
    with pytest.raises(ValueError, match="Height must be positive"):
        bsa_from_cm(70, 0)

    with pytest.raises(ValueError, match="Height must be positive"):
        bsa_from_cm(70, -175)


def test_bsa_precision():
    """Test BSA calculation precision (rounded to 2 decimal places)."""
    result = bsa_mosteller(70.123, 1.754)
    # Should be rounded to 2 decimal places
    assert len(str(result).split(".")[-1]) <= 2


def test_bsa_realistic_scenarios():
    """Test BSA with realistic medical scenarios."""
    # Pediatric patient (10 years old)
    child_bsa = bsa_mosteller(30, 1.35)
    assert 0.8 <= child_bsa <= 1.2

    # Adult athlete
    athlete_bsa = bsa_mosteller(85, 1.85)
    assert 1.9 <= athlete_bsa <= 2.3

    # Elderly patient
    elderly_bsa = bsa_mosteller(65, 1.65)
    assert 1.5 <= elderly_bsa <= 1.8


def test_bsa_formula_consistency():
    """Test that different formulas give reasonably similar results."""
    weight, height = 70, 1.75
    results = bsa_all_formulas(weight, height)

    values = list(results.values())
    min_val = min(values)
    max_val = max(values)

    # All formulas should be within reasonable range of each other
    assert (max_val - min_val) < 0.1, f"Formulas vary too much: {results}"


def test_bsa_dubois_negative_weight():
    """Test BSA DuBois calculation with negative weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_dubois(-70, 1.75)


def test_bsa_dubois_zero_weight():
    """Test BSA DuBois calculation with zero weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_dubois(0, 1.75)


def test_bsa_dubois_negative_height():
    """Test BSA DuBois calculation with negative height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_dubois(70, -1.75)


def test_bsa_dubois_zero_height():
    """Test BSA DuBois calculation with zero height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_dubois(70, 0)


def test_bsa_haycock_negative_weight():
    """Test BSA Haycock calculation with negative weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_haycock(-70, 1.75)


def test_bsa_haycock_zero_weight():
    """Test BSA Haycock calculation with zero weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_haycock(0, 1.75)


def test_bsa_haycock_negative_height():
    """Test BSA Haycock calculation with negative height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_haycock(70, -1.75)


def test_bsa_haycock_zero_height():
    """Test BSA Haycock calculation with zero height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_haycock(70, 0)


def test_bsa_gehan_george_negative_weight():
    """Test BSA Gehan-George calculation with negative weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_gehan_george(-70, 1.75)


def test_bsa_gehan_george_zero_weight():
    """Test BSA Gehan-George calculation with zero weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_gehan_george(0, 1.75)


def test_bsa_gehan_george_negative_height():
    """Test BSA Gehan-George calculation with negative height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_gehan_george(70, -1.75)


def test_bsa_gehan_george_zero_height():
    """Test BSA Gehan-George calculation with zero height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_gehan_george(70, 0)


def test_bsa_boyd_negative_weight():
    """Test BSA Boyd calculation with negative weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_boyd(-70, 1.75)


def test_bsa_boyd_zero_weight():
    """Test BSA Boyd calculation with zero weight."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_boyd(0, 1.75)


def test_bsa_boyd_negative_height():
    """Test BSA Boyd calculation with negative height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_boyd(70, -1.75)


def test_bsa_boyd_zero_height():
    """Test BSA Boyd calculation with zero height."""
    with pytest.raises(ValueError, match="Weight and height must be positive"):
        bsa_boyd(70, 0)


def test_bsa_unknown_formula():
    """Test BSA calculation with unknown formula."""

    with pytest.raises(ValueError, match="Unknown BSA formula"):
        bsa(70, 1.75, "invalid formula")
