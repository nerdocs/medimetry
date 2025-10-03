def test_dob2age_birthday_not_occurred_this_year():
    """Test that age calculation is correct when birthday has not occurred this year."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on December 15, 1990, current date is October 10, 2023
    # Birthday hasn't occurred yet this year
    dob = date(1990, 12, 15)
    given_date = date(2023, 10, 10)

    result = dob2age(dob, given_date)
    assert result == 32  # Should be 32, not 33, since birthday hasn't occurred


def test_dob2age_birthday_already_occurred_this_year():
    """Test that age calculation is correct when birthday has already occurred this year."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on March 15, 1990, current date is October 10, 2023
    # Birthday has already occurred this year
    dob = date(1990, 3, 15)
    given_date = date(2023, 10, 10)

    result = dob2age(dob, given_date)
    assert result == 33  # Should be 33 since birthday has already occurred


def test_dob2age_today_is_birthday():
    """Test that age calculation is correct when today is exactly the birthday."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on October 15, 1990, current date is October 15, 2023
    # Today is exactly their birthday
    dob = date(1990, 10, 15)
    given_date = date(2023, 10, 15)

    result = dob2age(dob, given_date)
    assert result == 33  # Should be 33 since it's their 33rd birthday


def test_dob2age_date_of_birth_is_today():
    """Test that age calculation returns 0 when date of birth is today."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born today
    today = date(2023, 10, 15)
    dob = date(2023, 10, 15)

    result = dob2age(dob, today)
    assert result == 0


def test_dob2age_leap_year_birth_dates():
    """Test that age calculation handles leap year birth dates correctly."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on leap day February 29, 2000
    # Test on February 28, 2023 (non-leap year)
    dob = date(2000, 2, 29)
    given_date = date(2023, 2, 28)

    result = dob2age(dob, given_date)
    assert result == 22  # Should be 22, birthday hasn't occurred yet

    # Test on March 1, 2023 (day after would-be leap day)
    given_date = date(2023, 3, 1)
    result = dob2age(dob, given_date)
    assert result == 23  # Should be 23, birthday has effectively occurred


def test_dob2age_with_given_date_parameter():
    """Test that age calculation uses provided given_date parameter instead of today."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on June 15, 1985
    dob = date(1985, 6, 15)
    # Provide a specific date instead of using today
    given_date = date(2020, 8, 20)

    result = dob2age(dob, given_date)
    assert result == 35  # Should be 35 based on the given_date, not current date


def test_dob2age_december_birth_january_current():
    """Test that age calculation is correct when birth month is December and current month is January."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on December 25, 1990, current date is January 15, 2024
    # Birth month is December, current month is January (next year)
    dob = date(1990, 12, 25)
    given_date = date(2024, 1, 15)

    result = dob2age(dob, given_date)
    assert result == 33  # Should be 33 since birthday has already occurred


def test_dob2age_same_month_different_days():
    """Test that age calculation is correct when birth date and current date are in the same month but different days."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on October 20, 1990, current date is October 10, 2023
    # Same month but birthday hasn't occurred yet (current day < birth day)
    dob = date(1990, 10, 20)
    given_date = date(2023, 10, 10)

    result = dob2age(dob, given_date)
    assert result == 32  # Should be 32, not 33, since birthday hasn't occurred yet

    # Person born on October 5, 1990, current date is October 10, 2023
    # Same month but birthday has already occurred (current day > birth day)
    dob = date(1990, 10, 5)
    given_date = date(2023, 10, 10)

    result = dob2age(dob, given_date)
    assert result == 33  # Should be 33 since birthday has already occurred


def test_dob2age_leap_year_february_29th():
    """Test that age calculation is correct for someone born on February 29th in a leap year."""
    from datetime import date

    from medimetry.converters import dob2age

    # Person born on February 29, 2000 (leap year)
    dob = date(2000, 2, 29)

    # Test on February 28, 2024 (leap year, day before birthday)
    given_date = date(2024, 2, 28)
    result = dob2age(dob, given_date)
    assert result == 23  # Should be 23, birthday hasn't occurred yet

    # Test on February 29, 2024 (leap year, exact birthday)
    given_date = date(2024, 2, 29)
    result = dob2age(dob, given_date)
    assert result == 24  # Should be 24, it's their 24th birthday

    # Test on March 1, 2024 (leap year, day after birthday)
    given_date = date(2024, 3, 1)
    result = dob2age(dob, given_date)
    assert result == 24  # Should be 24, birthday has occurred


# -----------------------------------------------


def test_dob2age_tuple_birthday_not_occurred_this_year():
    """Test that age tuple calculation is correct when birthday has not occurred this year."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on December 15, 1990, current date is October 10, 2023
    # Birthday hasn't occurred yet this year
    dob = date(1990, 12, 15)
    given_date = date(2023, 10, 10)

    result = dob2age_tuple(dob, given_date)
    assert result == (32, 9, 25)  # 32 years, 9 months, 25 days


def test_dob2age_tuple_birthday_already_occurred_this_year():
    """Test that age tuple calculation is correct when birthday has already occurred this year."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on March 15, 1990, current date is October 10, 2023
    # Birthday has already occurred this year
    dob = date(1990, 3, 15)
    given_date = date(2023, 10, 10)

    result = dob2age_tuple(dob, given_date)
    assert result == (33, 6, 25)  # 33 years, 6 months, 25 days


def test_dob2age_tuple_today_is_birthday():
    """Test that age tuple calculation is correct when today is exactly the birthday."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on October 15, 1990, current date is October 15, 2023
    # Today is exactly their birthday
    dob = date(1990, 10, 15)
    given_date = date(2023, 10, 15)

    result = dob2age_tuple(dob, given_date)
    assert result == (33, 0, 0)  # Should be exactly 33 years, 0 months, 0 days


def test_dob2age_tuple_date_of_birth_is_today():
    """Test that age tuple calculation returns (0, 0, 0) when date of birth is today."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born today
    today = date(2023, 10, 15)
    dob = date(2023, 10, 15)

    result = dob2age_tuple(dob, today)
    assert result == (0, 0, 0)


def test_dob2age_tuple_negative_days_adjustment():
    """Test that age tuple calculation handles negative days correctly when current day is less than birth day."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on March 25, 1990, current date is April 10, 2023
    # Current day (10) is less than birth day (25), so days should be negative initially
    # Should adjust by borrowing from previous month
    dob = date(1990, 3, 25)
    given_date = date(2023, 4, 10)

    result = dob2age_tuple(dob, given_date)
    # March has 31 days, so: 10 - 25 = -15, then -15 + 31 = 16 days
    # Months: 4 - 3 - 1 (borrowed) = 0 months
    # Years: 2023 - 1990 = 33 years
    assert result == (33, 0, 16)


def test_dob2age_tuple_negative_months_adjustment():
    """Test that age tuple calculation handles negative months correctly when current month is less than birth month."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on October 15, 1990, current date is March 20, 2023
    # Current month (3) is less than birth month (10), so months should be negative initially
    # Should adjust by borrowing from years
    dob = date(1990, 10, 15)
    given_date = date(2023, 3, 20)

    result = dob2age_tuple(dob, given_date)
    # Months: 3 - 10 = -7, then -7 + 12 = 5 months
    # Years: 2023 - 1990 - 1 (borrowed) = 32 years
    # Days: 20 - 15 = 5 days
    assert result == (32, 5, 5)


def test_dob2age_tuple_negative_days_january_to_december():
    """Test that age tuple calculation handles negative days in January by going to December of previous year."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on January 25, 1990, current date is January 10, 2023
    # Current day (10) is less than birth day (25) in January
    # Should adjust by borrowing from December of previous year
    dob = date(1990, 1, 25)
    given_date = date(2023, 1, 10)

    result = dob2age_tuple(dob, given_date)
    # Days: 10 - 25 = -15, then -15 + 31 (December has 31 days) = 16 days
    # Months: 1 - 1 - 1 (borrowed) = -1, then -1 + 12 = 11 months
    # Years: 2023 - 1990 - 1 (borrowed) = 32 years
    assert result == (32, 11, 16)


def test_dob2age_tuple_february_leap_year_monthrange():
    """Test that age tuple calculation uses monthrange correctly for February in leap years."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on February 29, 2000 (leap year), current date is March 10, 2024 (leap year)
    # Days: 10 - 29 = -19, needs to borrow from February 2024 (29 days in leap year)
    # Should result in -19 + 29 = 10 days
    dob = date(2000, 2, 29)
    given_date = date(2024, 3, 10)

    result = dob2age_tuple(dob, given_date)
    # Days: 10 - 29 = -19, then -19 + 29 (February 2024 has 29 days) = 10 days
    # Months: 3 - 2 - 1 (borrowed) = 0 months
    # Years: 2024 - 2000 = 24 years
    assert result == (24, 0, 10)


def test_dob2age_tuple_february_non_leap_year():
    """Test that age tuple calculation handles February correctly in non-leap years using monthrange."""
    from datetime import date

    from medimetry.converters import dob2age_tuple

    # Person born on March 5, 2000, current date is February 1, 2023 (non-leap year)
    # Should use January 2023 which has 31 days for calculation
    dob = date(2000, 3, 5)
    given_date = date(2023, 2, 1)

    result = dob2age_tuple(dob, given_date)
    # Days: 1 - 5 = -4, then -4 + 31 (January 2023 has 31 days) = 27 days
    # Months: 2 - 3 - 1 (borrowed) = -2, then -2 + 12 = 10 months
    # Years: 2023 - 2000 - 1 (borrowed) = 22 years
    assert result == (22, 10, 27)  # 22 years, 10 months, 27 days


def test_dob2age_tuple_uses_today_when_given_date_is_none():
    """Test that dob2age_tuple uses datetime.now().date() when given_date parameter is None."""
    from datetime import date
    from unittest.mock import patch

    from medimetry.converters import dob2age_tuple

    # Mock datetime.now().date() to return a specific date
    mock_today = date(2023, 10, 15)

    with patch("medimetry.converters.datetime") as mock_datetime:
        mock_datetime.now.return_value.date.return_value = mock_today

        # Person born on March 15, 1990
        dob = date(1990, 3, 15)

        # Call without given_date parameter (should use mocked today)
        result = dob2age_tuple(dob)

        # Verify the calculation uses the mocked today date
        expected = (33, 7, 0)  # 33 years, 7 months, 0 days from 1990-03-15 to 2023-10-15
        assert result == expected

        # Verify datetime.now().date() was called
        mock_datetime.now.assert_called_once()
        mock_datetime.now.return_value.date.assert_called_once()
