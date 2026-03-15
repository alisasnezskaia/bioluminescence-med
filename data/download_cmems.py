"""
Download CMEMS Mediterranean data: SST, chlorophyll-a, currents, mixed layer depth.

Data source: Copernicus Marine Service (marine.copernicus.eu)
Requires a free CMEMS account. Set credentials in .env:
    CMEMS_USER=your_username
    CMEMS_PASSWORD=your_password

Products used:
    - SST:        CMEMS-SST-MED-L4-NRT-OBSERVATIONS (daily, 0.05°)
    - CHL + MLD:  MEDSEA_MULTIYEAR_BGC_006_008 (daily, 0.042°)
    - Currents:   MEDSEA_MULTIYEAR_PHY_006_004 (daily, 0.042°)

Usage:
    python data/download_cmems.py --start 2015-01-01 --end 2023-12-31
"""

import argparse
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path("data/raw/cmems")

# Mediterranean bounding box
MED_BBOX = {
    "lon_min": -6.0,
    "lon_max": 36.5,
    "lat_min": 30.0,
    "lat_max": 46.0,
}

PRODUCTS = {
    "sst": {
        "service_id": "CMEMS-SST-MED-L4-NRT-OBSERVATIONS-010-004-a",
        "product_id": "cmems_obs-sst_med_phy-sst_nrt_l4-0.05deg_P1D-m",
        "variable": "analysed_sst",
        "subdir": "sst",
    },
    "chl": {
        "service_id": "MEDSEA_MULTIYEAR_BGC_006_008-TDS",
        "product_id": "cmems_mod_med_bgc-bio_my_4.2km_P1D-m",
        "variable": "chl",
        "subdir": "chl",
    },
    "mld": {
        "service_id": "MEDSEA_MULTIYEAR_PHY_006_004-TDS",
        "product_id": "cmems_mod_med_phy-mld_my_4.2km_P1D-m",
        "variable": "mlotst",
        "subdir": "mld",
    },
}


def download_product(product_key: str, start: str, end: str):
    p = PRODUCTS[product_key]
    out_dir = OUTPUT_DIR / p["subdir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{product_key}_{start}_{end}.nc"

    user = os.environ.get("CMEMS_USER")
    pw   = os.environ.get("CMEMS_PASSWORD")

    if not user or not pw:
        raise EnvironmentError(
            "Set CMEMS_USER and CMEMS_PASSWORD in .env
"
            "Register free at: https://marine.copernicus.eu"
        )

    cmd = [
        "motuclient",
        "--motu", "https://nrt.cmems-du.eu/motu-web/Motu",
        "--service-id",  p["service_id"],
        "--product-id",  p["product_id"],
        "--longitude-min", str(MED_BBOX["lon_min"]),
        "--longitude-max", str(MED_BBOX["lon_max"]),
        "--latitude-min",  str(MED_BBOX["lat_min"]),
        "--latitude-max",  str(MED_BBOX["lat_max"]),
        "--date-min", f"{start} 00:00:00",
        "--date-max", f"{end} 23:59:59",
        "--variable",    p["variable"],
        "--out-dir",     str(out_dir),
        "--out-name",    out_file.name,
        "--user",        user,
        "--pwd",         pw,
    ]

    print(f"Downloading {product_key}: {start} → {end}")
    subprocess.run(cmd, check=True)
    print(f"  Saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start",    default="2015-01-01")
    parser.add_argument("--end",      default="2023-12-31")
    parser.add_argument("--products", nargs="+", default=list(PRODUCTS.keys()),
                        choices=list(PRODUCTS.keys()))
    args = parser.parse_args()

    for key in args.products:
        download_product(key, args.start, args.end)
