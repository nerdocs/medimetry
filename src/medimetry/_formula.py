"""The record that describes a formula, and the rounding every formula shares.

Kept apart from :mod:`medimetry.formulas` (the registry) so that the domain
modules can declare their records without importing the registry.
"""

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from decimal import ROUND_HALF_UP
from decimal import Decimal


@dataclass(frozen=True)
class FormulaInfo:
    """What a consumer needs to know about a formula without reading its docstring.

    Attributes:
        id: Stable identifier, equal to the function's name (``"ckd_epi_2021"``). Store it to say which formula
            produced a value.
        name: Display name in English (``"eGFR (CKD-EPI 2021)"``).
        function: The function computing it.
        unit: UCUM code of the result (``"mL/min/{1.73_m2}"``, ``"1"`` for a dimensionless value).
        inputs: UCUM code per argument that carries a unit (``{"creatinine": "mg/dL"}``) — convert into these
            before calling.
        digits: Places of the customary display, used by ``rounded=True``.
        citation: The publication the implementation follows.
        loinc: LOINC code of the result, where one exists and is known; ``None`` otherwise.
        input_loinc: LOINC code per argument that is itself a measurement (``{"creatinine": "2160-0"}``), in the
            unit of ``inputs``; lets a consumer find the value to pass.
        min_age: Lowest age in years of the published domain; the function raises ``ValueError`` below it.
            ``None`` where the publication states none.
    """

    id: str
    name: str
    function: Callable[..., float]
    unit: str
    inputs: dict[str, str]
    digits: int
    citation: str
    loinc: str | None = None
    min_age: float | None = None
    input_loinc: dict[str, str] = field(default_factory=dict)


def half_up(value: float, digits: int) -> float:
    """Round ``value`` to ``digits`` places, halves away from zero (``2.25`` → ``2.3``).

    Python's ``round()`` rounds halves to the even digit and works on the binary float; this rounds the decimal
    value as it is written, the way a printed table does.

    >>> half_up(2.25, 1)
    2.3
    >>> half_up(-4.75, 1)
    -4.8
    """
    return float(Decimal(repr(value)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))


def check_age(info: FormulaInfo, age: float) -> None:
    """Raise ``ValueError`` when ``age`` lies below the formula's published domain."""
    if info.min_age is not None and age < info.min_age:
        raise ValueError(f"{info.name} is only defined from {info.min_age:g} years of age: {age}")
