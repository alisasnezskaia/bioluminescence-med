"""
Download bioluminescence ship observation data from MBARI and related sources.

Primary source: MBARI Bioluminescence Database
    https://www.mbari.org/science/upper-ocean-systems/bioluminescence/

Secondary: NOAA World Ocean Database (filtered for bioluminescence flags)
    https://www.ncei.noaa.gov/products/world-ocean-database

These are sparse point observations from research vessels — they form
the ground truth labels for the probability model.

Usage:
    python data/download_mbari.py
"""

import json
from pathlib import Path
import urllib.request

OUTPUT_DIR = Path("data/raw/mbari")

# MBARI bioluminescence measurement archive (CSV format)
# This URL points to a curated subset for the Mediterranean and adjacent Atlantic
# Check https://www.mbari.org/bioluminescence for the latest version
MBARI_URL = (
    "https://www.mbari.org/wp-content/uploads/bioluminescence/"
    "biolum_observations_mediterranean.csv"
)


def download_mbari():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / "mbari_biolum_med.csv"

    print("Downloading MBARI bioluminescence observations...")
    print("Note: if the URL above returns 404, download manually from:")
    print("  https://www.mbari.org/science/upper-ocean-systems/bioluminescence/")
    print()

    try:
        urllib.request.urlretrieve(MBARI_URL, out_file)
        print(f"Saved to {out_file}")
    except Exception as e:
        print(f"Auto-download failed ({e}).")
        print("Please download the dataset manually and place it at:")
        print(f"  {out_file}")
        print()
        print("A synthetic placeholder will be created so the notebooks can run.")
        _create_placeholder(out_file)


def _create_placeholder(out_file: Path):
    """
    Creates a small synthetic placeholder with the right schema
    so the notebooks run without real data.
    Placeholder rows are clearly labelled as synthetic.
    """
    import csv
    rows = [
        ["date", "lat", "lon", "biolum_photons_s", "source", "synthetic"],
        ["2016-08-14", 43.5, 7.8, 2.4e10, "MBARI_placeholder", "True"],
        ["2017-06-22", 41.2, 14.3, 8.1e9,  "MBARI_placeholder", "True"],
        ["2018-09-03", 44.0, 13.1, 5.5e10, "MBARI_placeholder", "True"],
        ["2019-07-11", 38.4, 15.8, 1.2e10, "MBARI_placeholder", "True"],
        ["2020-08-29", 42.7, 9.2,  3.8e10, "MBARI_placeholder", "True"],
    ]
    with open(out_file, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"Placeholder saved to {out_file}")
    print("Replace with real observations before training the model.")


if __name__ == "__main__":
    download_mbari()
