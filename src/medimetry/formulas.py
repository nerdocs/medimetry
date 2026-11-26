"""Every formula of the library by its stable id, with what a consumer needs to call it and to label its result.

A consumer that stores a computed value stores ``FormulaInfo.id`` beside it; ``formula(id)`` gives the record back,
including the function. Ids equal the function names and do not change for a published equation — a newer
equation gets a new id (``ckd_epi_2021``), and convenience names such as ``ckd_epi`` are no ids.

>>> formula("ckd_epi_2021").inputs
{'creatinine': 'mg/dL'}
"""

from medimetry._formula import FormulaInfo
from medimetry.anthropometric import BMI
from medimetry.anthropometric import BSA_BOYD
from medimetry.anthropometric import BSA_DUBOIS
from medimetry.anthropometric import BSA_GEHAN_GEORGE
from medimetry.anthropometric import BSA_HAYCOCK
from medimetry.anthropometric import BSA_MOSTELLER
from medimetry.cardiac import QTC
from medimetry.cardiovasc import MEAN_ARTERIAL_PRESSURE
from medimetry.growth import GROWTH_PERCENTILE
from medimetry.growth import GROWTH_ZSCORE
from medimetry.laboratory import ZLOG
from medimetry.lytes import CALCIUM_CORRECTION
from medimetry.renal import ACR
from medimetry.renal import CKD_EPI_2009
from medimetry.renal import CKD_EPI_2021
from medimetry.renal import CKD_EPI_2021_CYSTATIN
from medimetry.renal import COCKCROFT_GAULT
from medimetry.renal import EKFC
from medimetry.renal import EKFC_CYSTATIN
from medimetry.renal import KFRE_2_YEAR
from medimetry.renal import KFRE_5_YEAR
from medimetry.renal import MDRD

__all__ = ["FORMULAS", "FormulaInfo", "formula"]

FORMULAS: dict[str, FormulaInfo] = {
    info.id: info
    for info in (
        ACR,
        COCKCROFT_GAULT,
        MDRD,
        CKD_EPI_2021,
        CKD_EPI_2021_CYSTATIN,
        CKD_EPI_2009,
        EKFC,
        EKFC_CYSTATIN,
        KFRE_2_YEAR,
        KFRE_5_YEAR,
        BMI,
        BSA_DUBOIS,
        BSA_MOSTELLER,
        BSA_HAYCOCK,
        BSA_GEHAN_GEORGE,
        BSA_BOYD,
        QTC,
        MEAN_ARTERIAL_PRESSURE,
        CALCIUM_CORRECTION,
        ZLOG,
        GROWTH_ZSCORE,
        GROWTH_PERCENTILE,
    )
}


def formula(formula_id: str) -> FormulaInfo:
    """The record of ``formula_id``; ``ValueError`` for an id the library does not know."""
    try:
        return FORMULAS[formula_id]
    except KeyError:
        raise ValueError(f"Unknown formula: {formula_id}") from None
