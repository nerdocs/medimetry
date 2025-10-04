import pytest

from medimetry.anthropometric import BMICategory
from medimetry.anthropometric import bmi
from medimetry.anthropometric import bmi_category
from medimetry.anthropometric import bmi_from_cm
from medimetry.anthropometric import bmi_with_category
from medimetry.anthropometric import bmi_with_category_cm


def test_bmi_normal_calculation():
    """Test BMI calculation with normal values."""
    # 70 kg, 1.75 m = 22.9 BMI
    result = bmi(70, 1.75)
    assert result == 22.9


def test_bmi_from_cm_calculation():
    """Test BMI calculation with height in centimeters."""
    # 70 kg, 175 cm = 22.9 BMI
    result = bmi_from_cm(70, 175)
    assert result == 22.9


def test_bmi_rounding():
    """Test that BMI is rounded to 1 decimal place."""
    # 68 kg, 1.73 m = 22.72... should round to 22.7
    result = bmi(68, 1.73)
    assert result == 22.7


def test_bmi_category_underweight():
    """Test BMI category classification for underweight."""
    category = bmi_category(17.5)
    assert category == BMICategory.UNDERWEIGHT


def test_bmi_category_normal():
    """Test BMI category classification for normal weight."""
    category = bmi_category(22.0)
    assert category == BMICategory.NORMAL


def test_bmi_category_overweight():
    """Test BMI category classification for overweight."""
    category = bmi_category(27.5)
    assert category == BMICategory.OVERWEIGHT


def test_bmi_category_obese_class_i():
    """Test BMI category classification for obese class I."""
    category = bmi_category(32.5)
    assert category == BMICategory.OBESE_CLASS_I


def test_bmi_category_obese_class_ii():
    """Test BMI category classification for obese class II."""
    category = bmi_category(37.5)
    assert category == BMICategory.OBESE_CLASS_II


def test_bmi_category_obese_class_iii():
    """Test BMI category classification for obese class III."""
    category = bmi_category(42.5)
    assert category == BMICategory.OBESE_CLASS_III


def test_bmi_category_boundaries():
    """Test BMI category boundaries."""
    # Underweight/Normal boundary (18.5)
    assert bmi_category(18.4) == BMICategory.UNDERWEIGHT
    assert bmi_category(18.5) == BMICategory.NORMAL

    # Normal/Overweight boundary (25.0)
    assert bmi_category(24.9) == BMICategory.NORMAL
    assert bmi_category(25.0) == BMICategory.OVERWEIGHT

    # Overweight/Obese I boundary (30.0)
    assert bmi_category(29.9) == BMICategory.OVERWEIGHT
    assert bmi_category(30.0) == BMICategory.OBESE_CLASS_I

    # Obese I/II boundary (35.0)
    assert bmi_category(34.9) == BMICategory.OBESE_CLASS_I
    assert bmi_category(35.0) == BMICategory.OBESE_CLASS_II

    # Obese II/III boundary (40.0)
    assert bmi_category(39.9) == BMICategory.OBESE_CLASS_II
    assert bmi_category(40.0) == BMICategory.OBESE_CLASS_III


def test_bmi_with_category():
    """Test BMI calculation with category classification."""
    bmi_value, category = bmi_with_category(70, 1.75)
    assert bmi_value == 22.9
    assert category == BMICategory.NORMAL


def test_bmi_with_category_cm():
    """Test BMI calculation with category using centimeters."""
    bmi_value, category = bmi_with_category_cm(70, 175)
    assert bmi_value == 22.9
    assert category == BMICategory.NORMAL


def test_bmi_negative_weight():
    """Test that ValueError is raised for negative weight."""
    with pytest.raises(ValueError, match="Weight must be positive"):
        bmi(-70, 1.75)


def test_bmi_zero_weight():
    """Test that ValueError is raised for zero weight."""
    with pytest.raises(ValueError, match="Weight must be positive"):
        bmi(0, 1.75)


def test_bmi_negative_height():
    """Test that ValueError is raised for negative height."""
    with pytest.raises(ValueError, match="Height must be positive"):
        bmi(70, -1.75)


def test_bmi_zero_height():
    """Test that ValueError is raised for zero height."""
    with pytest.raises(ValueError, match="Height must be positive"):
        bmi(70, 0)


def test_bmi_from_cm_negative_height():
    """Test that ValueError is raised for negative height in cm."""
    with pytest.raises(ValueError, match="Height must be positive"):
        bmi_from_cm(70, -175)


def test_bmi_from_cm_zero_height():
    """Test that ValueError is raised for zero height in cm."""
    with pytest.raises(ValueError, match="Height must be positive"):
        bmi_from_cm(70, 0)


def test_bmi_category_negative():
    """Test that ValueError is raised for negative BMI value."""
    with pytest.raises(ValueError, match="BMI must be positive"):
        bmi_category(-22.0)


def test_bmi_category_zero():
    """Test that ValueError is raised for zero BMI value."""
    with pytest.raises(ValueError, match="BMI must be positive"):
        bmi_category(0)


def test_bmi_extreme_values():
    """Test BMI calculation with extreme but valid values."""
    # Very light person
    result1 = bmi(40, 1.80)
    assert result1 == 12.3
    assert bmi_category(result1) == BMICategory.UNDERWEIGHT

    # Very heavy person
    result2 = bmi(150, 1.70)
    assert result2 == 51.9
    assert bmi_category(result2) == BMICategory.OBESE_CLASS_III


def test_bmi_realistic_scenarios():
    """Test realistic BMI scenarios."""
    # Average adult male
    bmi_value1, category1 = bmi_with_category_cm(80, 180)
    assert bmi_value1 == 24.7
    assert category1 == BMICategory.NORMAL

    # Average adult female
    bmi_value2, category2 = bmi_with_category_cm(65, 165)
    assert bmi_value2 == 23.9
    assert category2 == BMICategory.NORMAL

    # Athlete with high muscle mass
    bmi_value3, category3 = bmi_with_category_cm(90, 180)
    assert bmi_value3 == 27.8
    assert category3 == BMICategory.OVERWEIGHT


def test_bmi_precision():
    """Test BMI calculation precision."""
    # Test that calculation maintains precision before rounding
    result = bmi(68.5, 1.732)  # Should be 22.82... rounded to 22.8
    assert result == 22.8


def test_bmi_enum_values():
    """Test that BMI category enum values are correct."""
    assert BMICategory.UNDERWEIGHT.value == "Underweight"
    assert BMICategory.NORMAL.value == "Normal weight"
    assert BMICategory.OVERWEIGHT.value == "Overweight"
    assert BMICategory.OBESE_CLASS_I.value == "Obese Class I"
    assert BMICategory.OBESE_CLASS_II.value == "Obese Class II"
    assert BMICategory.OBESE_CLASS_III.value == "Obese Class III"
