import math


def zlog(value: float, lower: float, upper: float) -> float:
    """
    Calculate the zlog value of a laboratory result.

    The zlog value re-expresses a result relative to its reference interval on a
    logarithmic scale: the lower limit maps to -1.96, the upper limit to +1.96,
    the interval's geometric centre to 0. The limits are taken as the 2.5th and
    97.5th percentiles of a log-normal reference population.

        zlog = (ln x - (ln LL + ln UL) / 2) * 3.92 / (ln UL - ln LL)

    Both limits must be the two limits of a reference interval. A one-sided
    interval (``< 5``) has no zlog value: Hoffmann rules out substituting a
    lower limit, so this function offers none.

    References:
        Hoffmann G, Klawonn F, Lichtinghagen R, Orth M. The zlog value as a basis for the
        standardization of laboratory results. LaboratoriumsMedizin. 2017;41(1):23-32.
        doi:10.1515/labmed-2016-0087

    Args:
        value (float): The result, in the unit of the interval
        lower (float): Lower reference limit (LL), same unit
        upper (float): Upper reference limit (UL), same unit

    Returns:
        float: The zlog value, unrounded

    >>> round(zlog(4.5, 4.5, 5.9), 2)
    -1.96
    >>> round(zlog(60.1, 80, 96), 2)
    -8.11
    """
    if value <= 0 or lower <= 0:
        raise ValueError("Value and lower limit must be positive")
    if upper <= lower:
        raise ValueError("Upper limit must be greater than the lower limit")

    log_lower = math.log(lower)
    log_upper = math.log(upper)
    return (math.log(value) - (log_lower + log_upper) / 2) * 3.92 / (log_upper - log_lower)
