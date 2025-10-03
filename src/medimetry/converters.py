from datetime import UTC
from datetime import date
from datetime import datetime


def umoll2mgdl(umoll: float) -> float:
    """
    Convert umol/L to mg/dL.

    Args:
        umoll (float): Concentration in umol/L

    Returns:
        float: Concentration in mg/dL
    """
    # assert that umoll is not infinitive
    if umoll == float("inf"):
        raise ValueError("Cannot convert infinity to mg/dL")
    if umoll == float("-inf"):
        raise ValueError("Cannot convert negative infinity to mg/dL")

    return umoll * 18.01528  # 18.01528 mg/mol


def mgdl2umoll(mgdl: float) -> float:
    """
    Convert mg/dL to umol/L.

    Args:
        mgdl (float): Concentration in mg/dL

    Returns:
        float: Concentration in umol/L
    """
    if mgdl == float("inf"):
        raise ValueError("Cannot convert infinity to mg/dL")
    if mgdl == float("-inf"):
        raise ValueError("Cannot convert negative infinity to mg/dL")
    return mgdl / 18.01528  # 18.01528 mg/mol


def dob2age(dob: date, given_date: date | None = None) -> int:
    """
    Convert date of birth to age in years.

    Args:
        dob (date): Date of birth

    Returns:
        int: Age in years
    """
    today: date = given_date or datetime.now(UTC).date()
    age_years = today.year - dob.year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age_years -= 1
    return age_years


def dob2age_tuple(dob: date, given_date: date | None = None) -> tuple[int, int, int]:
    """
    Convert date of birth to age in years, months, and days.

    Args:
        dob (date): Date of birth
        given_date (date, optional): Reference date for age calculation

    Returns:
        tuple: Age as (years, months, days)
    """
    today: date = given_date or datetime.now(UTC).date()

    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day

    # Adjust for negative days
    if days < 0:
        months -= 1
        # Get days in previous month
        if today.month == 1:
            prev_month_year = today.year - 1
            prev_month = 12
        else:
            prev_month_year = today.year
            prev_month = today.month - 1

        from calendar import monthrange

        days_in_prev_month = monthrange(prev_month_year, prev_month)[1]
        days += days_in_prev_month

    # Adjust for negative months
    if months < 0:
        years -= 1
        months += 12

    return (years, months, days)
