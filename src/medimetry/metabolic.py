from enum import Enum


class ChildPughGrade(Enum):
    """Child-Pugh classification grades."""

    A = "A"
    B = "B"
    C = "C"


class AscitesSeverity(Enum):
    """Ascites severity levels."""

    NONE = "none"
    SLIGHT = "slight"
    MODERATE = "moderate"


class EncephalopathyGrade(Enum):
    """Hepatic encephalopathy grades."""

    NONE = "none"
    GRADE1_2 = "grade1-2"
    GRADE3_4 = "grade3-4"


def child_pugh_score(
    bilirubin: float,
    albumin: float,
    inr: float,
    ascites: AscitesSeverity,
    encephalopathy: EncephalopathyGrade,
) -> tuple[int, ChildPughGrade]:
    """
    Calculate Child-Pugh score for liver disease severity assessment.

    Args:
        bilirubin (float): Total bilirubin in mg/dl
        albumin (float): Serum albumin in g/dl
        inr (float): International normalized ratio
        ascites (AscitesSeverity): Ascites severity level
        encephalopathy (EncephalopathyGrade): Hepatic encephalopathy grade

    Returns:
        tuple[int, ChildPughGrade]: Score (5-15) and corresponding grade (A/B/C)

    Raises:
        ValueError: If parameters are invalid
    """
    if bilirubin < 0:
        raise ValueError("Bilirubin must be non-negative")
    if albumin < 0:
        raise ValueError("Albumin must be non-negative")
    if inr < 0:
        raise ValueError("INR must be non-negative")

    if ascites not in AscitesSeverity:
        raise ValueError(f"Unsupported ascites severity: {ascites}")
    if encephalopathy not in EncephalopathyGrade:
        raise ValueError(f"Unsupported encephalopathy grade: {encephalopathy}")

    score = 0

    # Bilirubin scoring (mg/dl)
    if bilirubin < 2.0:
        score += 1
    elif bilirubin <= 3.0:
        score += 2
    else:
        score += 3

    # Albumin scoring (g/dl)
    if albumin > 3.5:
        score += 1
    elif albumin >= 2.8:
        score += 2
    else:
        score += 3

    # INR scoring
    if inr < 1.7:
        score += 1
    elif inr <= 2.3:
        score += 2
    else:
        score += 3

    # Ascites scoring
    if ascites == AscitesSeverity.NONE:
        score += 1
    elif ascites == AscitesSeverity.SLIGHT:
        score += 2
    else:  # moderate
        score += 3

    # Encephalopathy scoring
    if encephalopathy == EncephalopathyGrade.NONE:
        score += 1
    elif encephalopathy == EncephalopathyGrade.GRADE1_2:
        score += 2
    else:  # grade3-4
        score += 3

    # Determine grade
    if score <= 6:
        grade = ChildPughGrade.A
    elif score <= 9:
        grade = ChildPughGrade.B
    else:
        grade = ChildPughGrade.C

    return score, grade
