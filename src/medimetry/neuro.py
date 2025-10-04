from enum import Enum
from gettext import gettext as _


class EyeResponse(Enum):
    """Glasgow Coma Scale Eye Response."""

    NOT_TESTABLE = -20
    NONE = 1
    TO_PAIN = 2
    TO_VERBAL = 3
    SPONTANEOUS = 4


class VerbalResponse(Enum):
    """Glasgow Coma Scale Verbal Response."""

    NOT_TESTABLE = -20
    NONE = 1
    INCOMPREHENSIBLE_SOUNDS = 2
    INAPPROPRIATE_WORDS = 3
    CONFUSED = 4
    ORIENTED = 5


class MotorResponse(Enum):
    """Glasgow Coma Scale Motor Response."""

    NOT_TESTABLE = -20
    NONE = 1
    EXTENSION_TO_PAIN = 2
    FLEXION_TO_PAIN = 3
    WITHDRAWAL_FROM_PAIN = 4
    LOCALIZES_PAIN = 5
    OBEYS_COMMANDS = 6


class GCSCategory(Enum):
    """Glasgow Coma Scale severity categories."""

    SEVERE = _("Severe")
    MODERATE = _("Moderate")
    MILD = _("Mild")


def glasgow_coma_scale(
    eye_response: EyeResponse,
    verbal_response: VerbalResponse,
    motor_response: MotorResponse,
) -> tuple[int, GCSCategory]:
    """
    Calculate Glasgow Coma Scale score and severity category.

    Args:
        eye_response (EyeResponse): Eye opening response (1-4)
        verbal_response (VerbalResponse): Verbal response (1-5)
        motor_response (MotorResponse): Motor response (1-6)

    Returns:
        tuple[int, GCSCategory]: Total GCS score (3-15) and severity category

    Raises:
        ValueError: If invalid response values are provided
    """
    if not isinstance(eye_response, EyeResponse):
        raise ValueError("Eye response must be an EyeResponse enum")
    if not isinstance(verbal_response, VerbalResponse):
        raise ValueError("Verbal response must be a VerbalResponse enum")
    if not isinstance(motor_response, MotorResponse):
        raise ValueError("Motor response must be a MotorResponse enum")

    total_score = eye_response.value + verbal_response.value + motor_response.value

    # Determine severity category
    if total_score <= 8:
        category = GCSCategory.SEVERE
    elif total_score <= 12:
        category = GCSCategory.MODERATE
    else:
        category = GCSCategory.MILD

    return total_score, category


def gcs_from_scores(eye: int, verbal: int, motor: int) -> tuple[int, GCSCategory]:
    """
    Calculate Glasgow Coma Scale from integer scores.

    Args:
        eye (int): Eye opening response score (1-4)
        verbal (int): Verbal response score (1-5)
        motor (int): Motor response score (1-6)

    Returns:
        tuple[int, GCSCategory]: Total GCS score (3-15) and severity category

    Raises:
        ValueError: If scores are out of valid ranges
    """
    if not (1 <= eye <= 4):
        raise ValueError("Eye response must be between 1 and 4")
    if not (1 <= verbal <= 5):
        raise ValueError("Verbal response must be between 1 and 5")
    if not (1 <= motor <= 6):
        raise ValueError("Motor response must be between 1 and 6")

    eye_response = EyeResponse(eye)
    verbal_response = VerbalResponse(verbal)
    motor_response = MotorResponse(motor)

    return glasgow_coma_scale(eye_response, verbal_response, motor_response)
