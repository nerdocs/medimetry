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
) -> int:
    """
    Calculate the Child-Pugh score (sum of five items, 1-3 points each) as published by Pugh et al. (1973).

    References:
        Pugh RN, et al. Transection of the oesophagus for bleeding oesophageal varices.
        Br J Surg. 1973;60(8):646-649. doi:10.1002/bjs.1800600817

        Pugh 1973 grades the prothrombin time prolongation in seconds (< 4, 4-6, > 6 s).
        The INR bands used here (< 1.7, 1.7-2.3, > 2.3) are a commonly used conversion;
        their primary source could not be verified.

    Args:
        bilirubin (float): Total bilirubin in mg/dl
        albumin (float): Serum albumin in g/dl
        inr (float): International normalized ratio
        ascites (AscitesSeverity): Ascites severity level
        encephalopathy (EncephalopathyGrade): Hepatic encephalopathy grade

    Returns:
        int: Score (5-15)

    Raises:
        ValueError: If parameters are invalid

    >>> child_pugh_score(1.5, 3.8, 1.2, AscitesSeverity.NONE, EncephalopathyGrade.NONE)
    5
    """
    if bilirubin < 0:
        raise ValueError(f"Bilirubin must be non-negative: {bilirubin}")
    if albumin < 0:
        raise ValueError(f"Albumin must be non-negative: {albumin}")
    if inr < 0:
        raise ValueError(f"INR must be non-negative: {inr}")

    if not isinstance(ascites, AscitesSeverity):
        raise ValueError(f"Unsupported ascites severity: {ascites}")
    if not isinstance(encephalopathy, EncephalopathyGrade):
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

    return score


def child_pugh_category(score: int) -> ChildPughGrade:
    """
    Return the Child-Pugh grade of a Child-Pugh score: A 5-6, B 7-9, C 10-15.

    References:
        Pugh RN, et al. Transection of the oesophagus for bleeding oesophageal varices.
        Br J Surg. 1973;60(8):646-649. doi:10.1002/bjs.1800600817

    Args:
        score (int): Child-Pugh score (5-15), e.g. from ``child_pugh_score``

    Returns:
        ChildPughGrade: Grade A, B or C

    Raises:
        TypeError: If score is not an int
        ValueError: If score is outside 5-15

    >>> child_pugh_category(7)
    <ChildPughGrade.B: 'B'>
    """
    if not isinstance(score, int) or isinstance(score, bool):
        raise TypeError(f"Child-Pugh score must be an int: {score!r}")
    if not 5 <= score <= 15:
        raise ValueError(f"Child-Pugh score must be between 5 and 15: {score}")
    if score <= 6:
        return ChildPughGrade.A
    if score <= 9:
        return ChildPughGrade.B
    return ChildPughGrade.C
