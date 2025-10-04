import pytest

from medimetry.neuro import EyeResponse
from medimetry.neuro import GCSCategory
from medimetry.neuro import MotorResponse
from medimetry.neuro import VerbalResponse
from medimetry.neuro import gcs_from_scores
from medimetry.neuro import glasgow_coma_scale


def test_gcs_maximum_score():
    """Test GCS with maximum possible score (15) - mild injury."""
    score, category = glasgow_coma_scale(EyeResponse.SPONTANEOUS, VerbalResponse.ORIENTED, MotorResponse.OBEYS_COMMANDS)
    assert score == 15
    assert category == GCSCategory.MILD


def test_gcs_minimum_score():
    """Test GCS with minimum possible score (3) - severe injury."""
    score, category = glasgow_coma_scale(EyeResponse.NONE, VerbalResponse.NONE, MotorResponse.NONE)
    assert score == 3
    assert category == GCSCategory.SEVERE


def test_gcs_severe_boundary():
    """Test GCS severe category boundary (≤8)."""
    # Score of 8 (severe)
    score, category = glasgow_coma_scale(
        EyeResponse.TO_PAIN,  # 2
        VerbalResponse.INCOMPREHENSIBLE_SOUNDS,  # 2
        MotorResponse.WITHDRAWAL_FROM_PAIN,  # 4
    )
    assert score == 8
    assert category == GCSCategory.SEVERE


def test_gcs_moderate_boundary_low():
    """Test GCS moderate category lower boundary (9)."""
    score, category = glasgow_coma_scale(
        EyeResponse.TO_VERBAL,  # 3
        VerbalResponse.INCOMPREHENSIBLE_SOUNDS,  # 2
        MotorResponse.WITHDRAWAL_FROM_PAIN,  # 4
    )
    assert score == 9
    assert category == GCSCategory.MODERATE


def test_gcs_moderate_boundary_high():
    """Test GCS moderate category upper boundary (12)."""
    score, category = glasgow_coma_scale(
        EyeResponse.SPONTANEOUS,  # 4
        VerbalResponse.CONFUSED,  # 4
        MotorResponse.WITHDRAWAL_FROM_PAIN,  # 4
    )
    assert score == 12
    assert category == GCSCategory.MODERATE


def test_gcs_mild_boundary():
    """Test GCS mild category boundary (≥13)."""
    score, category = glasgow_coma_scale(
        EyeResponse.SPONTANEOUS,  # 4
        VerbalResponse.ORIENTED,  # 5
        MotorResponse.WITHDRAWAL_FROM_PAIN,  # 4
    )
    assert score == 13
    assert category == GCSCategory.MILD


def test_gcs_from_scores_valid():
    """Test GCS calculation from integer scores."""
    score, category = gcs_from_scores(4, 5, 6)
    assert score == 15
    assert category == GCSCategory.MILD


def test_gcs_from_scores_moderate():
    """Test GCS from scores resulting in moderate injury."""
    score, category = gcs_from_scores(3, 3, 4)
    assert score == 10
    assert category == GCSCategory.MODERATE


def test_gcs_from_scores_severe():
    """Test GCS from scores resulting in severe injury."""
    score, category = gcs_from_scores(1, 2, 3)
    assert score == 6
    assert category == GCSCategory.SEVERE


def test_gcs_invalid_eye_response():
    """Test that ValueError is raised for invalid eye response."""
    with pytest.raises(ValueError, match="Eye response must be an EyeResponse enum"):
        glasgow_coma_scale("invalid", VerbalResponse.ORIENTED, MotorResponse.OBEYS_COMMANDS)


def test_gcs_invalid_verbal_response():
    """Test that ValueError is raised for invalid verbal response."""
    with pytest.raises(ValueError, match="Verbal response must be a VerbalResponse enum"):
        glasgow_coma_scale(EyeResponse.SPONTANEOUS, "invalid", MotorResponse.OBEYS_COMMANDS)


def test_gcs_invalid_motor_response():
    """Test that ValueError is raised for invalid motor response."""
    with pytest.raises(ValueError, match="Motor response must be a MotorResponse enum"):
        glasgow_coma_scale(EyeResponse.SPONTANEOUS, VerbalResponse.ORIENTED, "invalid")


def test_gcs_from_scores_invalid_eye():
    """Test that ValueError is raised for invalid eye score."""
    with pytest.raises(ValueError, match="Eye response must be between 1 and 4"):
        gcs_from_scores(0, 3, 4)

    with pytest.raises(ValueError, match="Eye response must be between 1 and 4"):
        gcs_from_scores(5, 3, 4)


def test_gcs_from_scores_invalid_verbal():
    """Test that ValueError is raised for invalid verbal score."""
    with pytest.raises(ValueError, match="Verbal response must be between 1 and 5"):
        gcs_from_scores(3, 0, 4)

    with pytest.raises(ValueError, match="Verbal response must be between 1 and 5"):
        gcs_from_scores(3, 6, 4)


def test_gcs_from_scores_invalid_motor():
    """Test that ValueError is raised for invalid motor score."""
    with pytest.raises(ValueError, match="Motor response must be between 1 and 6"):
        gcs_from_scores(3, 3, 0)

    with pytest.raises(ValueError, match="Motor response must be between 1 and 6"):
        gcs_from_scores(3, 3, 7)


def test_gcs_all_combinations_valid():
    """Test that all valid GCS combinations produce scores between 3-15."""
    for eye in range(1, 5):
        for verbal in range(1, 6):
            for motor in range(1, 7):
                score, category = gcs_from_scores(eye, verbal, motor)
                assert 3 <= score <= 15
                assert category in [
                    GCSCategory.SEVERE,
                    GCSCategory.MODERATE,
                    GCSCategory.MILD,
                ]


def test_gcs_realistic_scenarios():
    """Test realistic clinical scenarios."""
    # Comatose patient
    score1, category1 = gcs_from_scores(1, 1, 2)  # No eye-opening, no verbal, abnormal extension
    assert score1 == 4
    assert category1 == GCSCategory.SEVERE

    # Confused patient
    score2, category2 = gcs_from_scores(4, 4, 5)  # Eyes open, confused speech, localizes pain
    assert score2 == 13
    assert category2 == GCSCategory.MILD

    # Moderate head injury
    score3, category3 = gcs_from_scores(3, 2, 4)  # Opens to voice, incomprehensible, withdraws
    assert score3 == 9
    assert category3 == GCSCategory.MODERATE
