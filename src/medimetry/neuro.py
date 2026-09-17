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

    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"


gcs_category_titles = {
    GCSCategory.SEVERE: _("Severe"),
    GCSCategory.MODERATE: _("Moderate"),
    GCSCategory.MILD: _("Mild"),
}


def glasgow_coma_scale(
    eye_response: EyeResponse,
    verbal_response: VerbalResponse,
    motor_response: MotorResponse,
) -> tuple[int, GCSCategory]:
    """
    Calculate Glasgow Coma Scale score and severity category.

    A total score is only defined when all three components are testable. If any
    component is NOT_TESTABLE, the components must be reported individually
    (e.g. "E4 VNT M6") and this function raises a ValueError.

    References:
        Teasdale G, Jennett B. Assessment of coma and impaired consciousness. A practical
        scale. Lancet. 1974;2(7872):81-84. doi:10.1016/s0140-6736(74)91639-0
        Teasdale G, et al. The Glasgow Coma Scale at 40 years: standing the test of time.
        Lancet Neurol. 2014;13(8):844-854. doi:10.1016/S1474-4422(14)70120-6

    Args:
        eye_response (EyeResponse): Eye opening response (1-4)
        verbal_response (VerbalResponse): Verbal response (1-5)
        motor_response (MotorResponse): Motor response (1-6)

    Returns:
        tuple[int, GCSCategory]: Total GCS score (3-15) and severity category

    Raises:
        ValueError: If invalid response values are provided or a component is not testable
    """
    if not isinstance(eye_response, EyeResponse):
        raise ValueError("Eye response must be an EyeResponse enum")
    if not isinstance(verbal_response, VerbalResponse):
        raise ValueError("Verbal response must be a VerbalResponse enum")
    if not isinstance(motor_response, MotorResponse):
        raise ValueError("Motor response must be a MotorResponse enum")
    if (
        eye_response == EyeResponse.NOT_TESTABLE
        or verbal_response == VerbalResponse.NOT_TESTABLE
        or motor_response == MotorResponse.NOT_TESTABLE
    ):
        raise ValueError("GCS total is undefined when a component is not testable; report the components individually")

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
