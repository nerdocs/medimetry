from enum import Enum


class Gender(Enum):
    MALE = "m"
    FEMALE = "f"
    DIVERSE = "d"


class EthnicalRace(Enum):
    AFRICAN_AMERICAN = "african_american"
    EUROPEAN = "european"
    OTHER = "other"


class QtcCorrectionType(Enum):
    BAZETT = "bazett"
    FRIDERICIA = "fridericia"
    FRAMINGHAM = "framingham"
    HODGES = "hodges"


class KfreRegion(Enum):
    """Calibration of the Kidney Failure Risk Equation (Tangri 2016): the baseline survival differs by region."""

    NORTH_AMERICA = "north_america"
    NON_NORTH_AMERICA = "non_north_america"
