from medimetry._formula import FormulaInfo
from medimetry._formula import half_up


def calcium_correction(total_calcium: float, albumin: float, *, rounded: bool = False) -> float:
    """
    Calculate albumin-corrected total serum calcium.

    Uses the formula: Corrected Ca = Total Ca - Albumin + 4.0 (Payne 1973)

    References:
        Payne RB, et al. Interpretation of serum calcium in patients with abnormal serum proteins.
        Br Med J. 1973;4(5893):643-646. doi:10.1136/bmj.4.5893.643

    Args:
        total_calcium (float): Total serum calcium in mg/dl
        albumin (float): Serum albumin in g/dl
        rounded (bool): Round to ``CALCIUM_CORRECTION.digits`` places (half up)

    Returns:
        float: Corrected calcium in mg/dl

    Raises:
        ValueError: If calcium or albumin values are negative
    """
    normal_albumin = 4.0
    if total_calcium < 0:
        raise ValueError("Total calcium must be non-negative")
    if albumin < 0:
        raise ValueError("Albumin must be non-negative")

    corrected_calcium = total_calcium - albumin + normal_albumin
    return half_up(corrected_calcium, CALCIUM_CORRECTION.digits) if rounded else corrected_calcium


CALCIUM_CORRECTION = FormulaInfo(
    id="calcium_correction",
    name="Albumin-corrected calcium (Payne)",
    function=calcium_correction,
    unit="mg/dL",
    inputs={"total_calcium": "mg/dL", "albumin": "g/dL"},
    digits=2,
    citation="Payne RB, et al. Br Med J. 1973;4(5893):643-646. doi:10.1136/bmj.4.5893.643",
)
