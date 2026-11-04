# read version from installed package
from importlib.metadata import version
__version__ = version("weather_ts3740")

from weather_ts3740.weather_ts3740 import (
    celsius_to_fahrenheit,
    clean_readings,
    summarize_temperatures,
)