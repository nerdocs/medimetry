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
