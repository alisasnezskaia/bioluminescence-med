"""
Download ERA5 reanalysis: 10m wind components and surface solar radiation.
PAR (photosynthetically active radiation) is derived from surface solar radiation.

Requires a free CDS account. Set up ~/.cdsapirc or use:
    https://cds.climate.copernicus.eu/api-how-to

Usage:
    python data/download_era5.py --start 2015 --end 2023
"""

import argparse
from pathlib import Path

import cdsapi

OUTPUT_DIR = Path("data/raw/era5")

# Mediterranean bounding box: N/W/S/E
MED_AREA = [46.0, -6.0, 30.0, 36.5]

VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "surface_solar_radiation_downwards",
]


def download_era5(start_year: int, end_year: int):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    c = cdsapi.Client()

    for year in range(start_year, end_year + 1):
        out_file = OUTPUT_DIR / f"era5_med_{year}.nc"
        print(f"Downloading ERA5 for {year}...")

        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": VARIABLES,
                "year":  str(year),
                "month": [f"{m:02d}" for m in range(1, 13)],
                "day":   [f"{d:02d}" for d in range(1, 32)],
                "time":  "12:00",
                "area":  MED_AREA,
                "format": "netcdf",
            },
            str(out_file),
        )
        print(f"  Saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2015)
    parser.add_argument("--end",   type=int, default=2023)
    args = parser.parse_args()

    download_era5(args.start, args.end)
