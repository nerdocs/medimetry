import pytest

from medimetry.pulmonary import perc_rule


def test_perc_rule_negative():
    """Test PERC rule with all criteria negative."""
    result = perc_rule(age=30, heart_rate=80, oxygen_saturation=98.0)

    assert result.positive_criteria == 0
    assert result.positive is False
    assert "PERC negative" in result.recommendation


def test_perc_rule_age_criterion():
    """Test PERC rule age criterion."""
    # Age < 50: negative
    result = perc_rule(age=45, heart_rate=80, oxygen_saturation=98.0)
    assert result.positive_criteria == 0
    assert result.positive is False

    # Age >= 50: positive
    result = perc_rule(age=50, heart_rate=80, oxygen_saturation=98.0)
    assert result.positive_criteria == 1
    assert result.positive is True


def test_perc_rule_heart_rate_criterion():
    """Test PERC rule heart rate criterion."""
    # HR < 100: negative
    result = perc_rule(age=30, heart_rate=95, oxygen_saturation=98.0)
    assert result.positive_criteria == 0
    assert result.positive is False

    # HR >= 100: positive
    result = perc_rule(age=30, heart_rate=100, oxygen_saturation=98.0)
    assert result.positive_criteria == 1
    assert result.positive is True


def test_perc_rule_oxygen_saturation_criterion():
    """Test PERC rule oxygen saturation criterion."""
    # O2 sat >= 95%: negative
    result = perc_rule(age=30, heart_rate=80, oxygen_saturation=95.0)
    assert result.positive_criteria == 0
    assert result.positive is False

    # O2 sat < 95%: positive
    result = perc_rule(age=30, heart_rate=80, oxygen_saturation=94.9)
    assert result.positive_criteria == 1
    assert result.positive is True


def test_perc_rule_all_criteria_positive():
    """Test PERC rule with all criteria positive."""
    result = perc_rule(
        age=60,  # >= 50
        heart_rate=110,  # >= 100
        oxygen_saturation=92.0,  # < 95
        unilateral_leg_swelling=True,
        hemoptysis=True,
        recent_surgery_trauma=True,
        prior_pe_dvt=True,
        hormone_use=True,
    )

    assert result.positive_criteria == 8
    assert result.positive is True
    assert "PERC positive (8 criteria)" in result.recommendation


def test_perc_rule_partial_positive():
    """Test PERC rule with some criteria positive."""
    result = perc_rule(
        age=55,  # positive
        heart_rate=80,  # negative
        oxygen_saturation=98.0,  # negative
        unilateral_leg_swelling=True,  # positive
        hemoptysis=False,  # negative
        recent_surgery_trauma=True,  # positive
        prior_pe_dvt=False,  # negative
        hormone_use=False,  # negative
    )

    assert result.positive_criteria == 3
    assert result.positive is True
    assert "PERC positive (3 criteria)" in result.recommendation


def test_perc_rule_invalid_age():
    """Test PERC rule with invalid age."""
    with pytest.raises(ValueError, match="Age must be positive"):
        perc_rule(age=0, heart_rate=80, oxygen_saturation=98.0)


def test_perc_rule_invalid_heart_rate():
    """Test PERC rule with invalid heart rate."""
    with pytest.raises(ValueError, match="Heart rate must be between 1 and 300 bpm"):
        perc_rule(age=30, heart_rate=0, oxygen_saturation=98.0)

    with pytest.raises(ValueError, match="Heart rate must be between 1 and 300 bpm"):
        perc_rule(age=30, heart_rate=350, oxygen_saturation=98.0)


def test_perc_rule_invalid_oxygen_saturation():
    """Test PERC rule with invalid oxygen saturation."""
    with pytest.raises(ValueError, match="Oxygen saturation must be between 0 and 100%"):
        perc_rule(age=30, heart_rate=80, oxygen_saturation=0)

    with pytest.raises(ValueError, match="Oxygen saturation must be between 0 and 100%"):
        perc_rule(age=30, heart_rate=80, oxygen_saturation=101)


def test_perc_rule_realistic_scenarios():
    """Test PERC rule with realistic clinical scenarios."""
    # Young healthy patient
    result = perc_rule(age=25, heart_rate=70, oxygen_saturation=99.0)
    assert result.positive is False

    # Elderly patient with tachycardia
    result = perc_rule(age=65, heart_rate=105, oxygen_saturation=96.0)
    assert result.positive_criteria == 2
    assert result.positive is True

    # Patient with multiple risk factors
    result = perc_rule(
        age=45,
        heart_rate=85,
        oxygen_saturation=97.0,
        prior_pe_dvt=True,
        hormone_use=True,
    )
    assert result.positive_criteria == 2
    assert result.positive is True
