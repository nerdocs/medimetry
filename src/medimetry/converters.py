from calendar import monthrange
from datetime import UTC
from datetime import date
from datetime import datetime


def dob2age(dob: date, given_date: date | None = None) -> int:
    """
    Convert date of birth to age in years.

    Args:
        dob (date): Date of birth
        given_date (date, optional): Reference date for age calculation

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

    >>> from datetime import date
    >>> dob2age_tuple(date(2025, 1, 31), date(2025, 3, 1))
    (0, 1, 1)
    """
    today: date = given_date or datetime.now(UTC).date()

    # Number of whole months between dob and today
    total_months = (today.year - dob.year) * 12 + today.month - dob.month
    if today.day < dob.day:
        total_months -= 1
    years, months = divmod(total_months, 12)

    # Anchor = dob shifted by the whole months, day clamped to the target month's length
    anchor_year = dob.year + (dob.month - 1 + total_months) // 12
    anchor_month = (dob.month - 1 + total_months) % 12 + 1
    anchor_day = min(dob.day, monthrange(anchor_year, anchor_month)[1])
    days = (today - date(anchor_year, anchor_month, anchor_day)).days

    return (years, months, days)
