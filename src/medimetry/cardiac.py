from medimetry._formula import FormulaInfo
from medimetry._formula import half_up
from medimetry.constants import QtcCorrectionType


def qtc_correction(
    qt_interval: float,
    heart_rate: int,
    formula: QtcCorrectionType = QtcCorrectionType.BAZETT,
    *,
    rounded: bool = False,
) -> float:
    """
    Calculate corrected QT interval (QTc) using various correction formulas.

    References:
        Bazett HC. An analysis of the time-relations of electrocardiograms. Heart. 1920;7:353-370.
        Fridericia LS. Die Systolendauer im Elektrokardiogramm bei normalen Menschen und bei
        Herzkranken. Acta Med Scand. 1920;53:469-486.
        Sagie A, et al. An improved method for adjusting the QT interval for heart rate
        (the Framingham Heart Study). Am J Cardiol. 1992;70(7):797-801.
        Hodges M, et al. Bazett's QT correction reviewed: evidence that a linear QT correction
        for heart rate is better. J Am Coll Cardiol. 1983;1:694.

    Args:
        qt_interval (float): QT interval in milliseconds
        heart_rate (int): Heart rate in beats per minute
        formula (QtcCorrectionType): Correction formula to use (QtcCorrectionType.BAZETT,
        QtcCorrectionType.FRIDERICIA, QtcCorrectionType.FRAMINGHAM,
        QtcCorrectionType.HODGES)
        rounded (bool): Round to ``QTC.digits`` places (half up)

    Returns:
        float: Corrected QT interval (QTc) in milliseconds

    Raises:
        ValueError: If QT interval or heart rate are invalid
        ValueError: If formula is not supported
    """
    if qt_interval <= 0:
        raise ValueError(f"QT interval must be positive: {qt_interval}")
    if heart_rate <= 0:
        raise ValueError(f"Heart rate must be positive: {heart_rate}")
    if heart_rate > 300:
        raise ValueError(f"Heart rate must be ≤ 300 bpm: {heart_rate}")

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

    return half_up(qtc, QTC.digits) if rounded else qtc


QTC = FormulaInfo(
    id="qtc_correction",
    name="Corrected QT interval",
    function=qtc_correction,
    unit="ms",
    inputs={"qt_interval": "ms", "heart_rate": "/min"},
    digits=1,
    citation="Bazett 1920, Fridericia 1920, Sagie 1992 (Framingham), Hodges 1983 — per QtcCorrectionType",
)
