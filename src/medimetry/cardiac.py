from medimetry.constants import QtcCorrectionType


def qtc_correction(
    qt_interval: float,
    heart_rate: int,
    formula: QtcCorrectionType = QtcCorrectionType.BAZETT,
) -> float:
    """
    Calculate corrected QT interval (QTc) using various correction formulas.

    Args:
        qt_interval (float): QT interval in milliseconds
        heart_rate (int): Heart rate in beats per minute
        formula (str): Correction formula to use (QtcCorrectionType.BAZETT,
        QtcCorrectionType.FRIDERICIA, QtcCorrectionType.FRAMINGHAM,
        QtcCorrectionType.HODGES)

    Returns:
        float: Corrected QT interval (QTc) in milliseconds, rounded to 1 decimal place

    Raises:
        ValueError: If QT interval or heart rate are invalid
        ValueError: If formula is not supported
    """
    if qt_interval <= 0:
        raise ValueError("QT interval must be positive")
    if heart_rate <= 0:
        raise ValueError("Heart rate must be positive")
    if heart_rate > 300:
        raise ValueError("Heart rate must be ≤ 300 bpm")

    # Convert heart rate to RR interval in seconds
    rr_interval = 60.0 / heart_rate

    if formula == QtcCorrectionType.BAZETT:
        # QTc = QT / √RR (most commonly used)
        qtc = qt_interval / (rr_interval**0.5)
    elif formula == QtcCorrectionType.FRIDERICIA:
        # QTc = QT / ∛RR (cube root)
        qtc = qt_interval / (rr_interval ** (1 / 3))
    elif formula == QtcCorrectionType.FRAMINGHAM:
        # QTc = QT + 154 x (1 - RR)
        qtc = qt_interval + 154 * (1 - rr_interval)
    elif formula == QtcCorrectionType.HODGES:
        # QTc = QT + 1.75 x (HR - 60)
        qtc = qt_interval + 1.75 * (heart_rate - 60)
    else:
        raise ValueError(
            f"Unsupported formula: {formula}. Use QtcCorrectionType.BAZETT, "
            "QtcCorrectionType.FRIDERICIA, QtcCorrectionType.FRAMINGHAM, "
            "QtcCorrectionType.HODGES"
        )

    return round(qtc, 1)
