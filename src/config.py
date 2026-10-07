"""Default assumptions taken from the supplied Climate Impact Report."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "climate_spatial_means_full.parquet"
OUTPUT_DIR = ROOT / "outputs"

# Default study settings from the report.
SCENARIO = "ssp585"
START_YEAR = 2025
END_YEAR = 2100

# Caledon Ski Club bounding box from the report.
LAT_N = 43.880
LAT_S = 43.850
LON_W = -79.950
LON_E = -79.900

# Good-day criteria from the report.
GOOD_DAY = {
    "tas": {"max": 265.0},          # K
    "hurs": {"max": 85.0},          # %
    "pr": {"max": 1.0 / 86400.0},   # kg m-2 s-1 ~= 1 mm/day
    "year": {"min": 2000, "max": 2100},
    "sfcWind": None,
    "rsds": None,
    "rlds": None,
    "huss": None,
    "tasmax": None,
    "tasmin": None,
}

# Bad-day criteria from the report.
BAD_DAY = {
    "tas": {"min": 283.0},          # K
    "pr": {"min": 5.0 / 86400.0},   # kg m-2 s-1 ~= 5 mm/day
    "hurs": {"min": 90.0},          # %
    "year": {"min": 2000, "max": 2100},
}

# Variables selected by the report for the main snowmaking analysis.
SNOWMAKING_VARIABLES = ["hurs", "pr", "tasmax"]

# Variables plotted in the future-trends section.
TREND_VARIABLES = ["hurs", "pr", "tasmax"]

VAR_META = {
    "tas": ("Air Temperature", "°C", lambda x: x - 273.15),
    "tasmax": ("Maximum Daily Temperature", "°C", lambda x: x - 273.15),
    "tasmin": ("Minimum Daily Temperature", "°C", lambda x: x - 273.15),
    "pr": ("Precipitation", "mm/day", lambda x: x * 86400.0),
    "hurs": ("Relative Humidity", "%", lambda x: x),
    "sfcWind": ("Surface Wind Speed", "m/s", lambda x: x),
    "rsds": ("Shortwave Radiation", "W/m²", lambda x: x),
    "rlds": ("Longwave Radiation", "W/m²", lambda x: x),
}
