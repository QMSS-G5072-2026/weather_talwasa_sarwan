import weather_ts3740


def test_version_is_defined():
    assert isinstance(weather_ts3740.__version__, str)

"""Tests for the weather_ts3740 package."""

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from weather_ts3740 import (
    celsius_to_fahrenheit,
    clean_readings,
    summarize_temperatures,
)

# =============================================================================
# UNIT TESTS
# =============================================================================


@pytest.mark.parametrize(
    "celsius, expected",
    [
        (0, 32.0),            # freezing
        (100, 212.0),         # boiling
        (-40, -40.0),         # scales meet
        (37, 98.6),           # body temperature (float rounding -> approx)
        (-273.15, -459.67),   # absolute zero is allowed
    ],
)
def test_celsius_to_fahrenheit(celsius, expected):
    """Known conversions match, using approx to allow for float rounding."""
    assert celsius_to_fahrenheit(celsius) == pytest.approx(expected)


@pytest.mark.parametrize(
    "bad_input, expected_error",
    [
        ("hot", TypeError),     # string
        (None, TypeError),      # None
        (True, TypeError),      # bool is explicitly rejected
        (-273.16, ValueError),  # just below absolute zero
    ],
)
def test_celsius_to_fahrenheit_invalid(bad_input, expected_error):
    """Invalid inputs raise the exception type given in the docstring."""
    with pytest.raises(expected_error):
        celsius_to_fahrenheit(bad_input)


def test_summarize_temperatures():
    """A list with one NaN is summarized correctly across all four keys."""
    # Arrange
    temps = [10.0, float("nan"), 20.0]

    # Act
    result = summarize_temperatures(temps)

    # Assert
    assert result["mean"] == pytest.approx(15.0)
    assert result["min"] == 10.0
    assert result["max"] == 20.0
    assert result["n_missing"] == 1

def test_summarize_temperatures_no_valid_readings():
    """A list with only NaN values raises ValueError."""
    with pytest.raises(ValueError):
        summarize_temperatures([float("nan"), float("nan")])
# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def raw_readings():
    """Unsorted station readings with one NaN and one 999.0 sensor error."""
    return pd.DataFrame(
        {
            "station": ["JFK", "CPK", "JFK", "CPK", "LGA"],
            "date": ["2026-07-02", "2026-07-01", "2026-07-01", "2026-07-02", "2026-07-01"],
            "temp_c": [30.0, 25.0, float("nan"), 999.0, 28.0],
        }
    )


def test_raw_readings_fixture(raw_readings):
    """The fixture has the expected columns, 5 rows, and exactly 1 missing temp."""
    assert list(raw_readings.columns) == ["station", "date", "temp_c"]
    assert len(raw_readings) == 5
    assert raw_readings["temp_c"].isna().sum() == 1


# =============================================================================
# TESTING DATAFRAMES
# =============================================================================


def test_clean_readings(raw_readings):
    """NaN and implausible rows are dropped, temp_f added, and rows sorted."""
    # Surviving rows: CPK 07-01 (25.0), JFK 07-02 (30.0), LGA 07-01 (28.0)
    expected = pd.DataFrame(
        {
            "station": ["CPK", "JFK", "LGA"],
            "date": ["2026-07-01", "2026-07-02", "2026-07-01"],
            "temp_c": [25.0, 30.0, 28.0],
            "temp_f": [77.0, 86.0, 82.4],
        }
    )

    result = clean_readings(raw_readings)

    assert_frame_equal(result, expected)