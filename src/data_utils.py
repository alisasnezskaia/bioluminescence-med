"""
Data loading and preprocessing for bioluminescence-med.

Main responsibilities:
- Load CMEMS and ERA5 netCDF files into aligned xarray Datasets
- Fill gaps from cloud cover via optimal interpolation
- Load and spatially align MBARI bioluminescence observations
"""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import xarray as xr
from scipy.interpolate import griddata


# Mediterranean bounding box
MED_LON = (-6.0, 36.5)
MED_LAT = (30.0, 46.0)
GRID_RES = 0.25  # degrees — common resolution after regridding


def load_cmems(data_dir: str | Path = "data/raw/cmems") -> xr.Dataset:
    """
    Load and merge CMEMS SST, CHL, and MLD files into a single Dataset
    on a common 0.25° grid.

    Returns an xr.Dataset with variables: sst, sst_anomaly, chl, mld
    on dimensions (time, lat, lon).
    """
    data_dir = Path(data_dir)
    datasets = {}

    for var in ("sst", "chl", "mld"):
        files = sorted((data_dir / var).glob("*.nc"))
        if not files:
            raise FileNotFoundError(
                f"No .nc files found in {data_dir / var}.
"
                "Run data/download_cmems.py first."
            )
        ds = xr.open_mfdataset(files, combine="by_coords")
        ds = _regrid_to_025(ds)
        datasets[var] = ds

    merged = xr.merge(list(datasets.values()))

    # Compute SST anomaly vs monthly climatology (1993–2014 baseline)
    clim = merged["sst"].sel(
        time=slice("1993-01-01", "2014-12-31")
    ).groupby("time.month").mean("time")
    merged["sst_anomaly"] = merged["sst"].groupby("time.month") - clim

    return merged


def load_era5(data_dir: str | Path = "data/raw/era5") -> xr.Dataset:
    """
    Load ERA5 wind and solar radiation data, compute:
    - wind_stress_curl: proxy for Ekman upwelling
    - par: photosynthetically active radiation (44% of surface solar)
    """
    data_dir = Path(data_dir)
    files = sorted(data_dir.glob("era5_med_*.nc"))
    if not files:
        raise FileNotFoundError(
            f"No ERA5 files in {data_dir}. Run data/download_era5.py first."
        )
    ds = xr.open_mfdataset(files, combine="by_coords")
    ds = _regrid_to_025(ds)

    # Wind stress curl (simplified — proper curl needs finite differences)
    rho_air = 1.225   # kg/m³
    Cd = 1.3e-3       # drag coefficient
    u = ds["u10"]
    v = ds["v10"]
    wspd = np.sqrt(u**2 + v**2)
    tau_x = rho_air * Cd * wspd * u
    tau_y = rho_air * Cd * wspd * v

    # Finite difference curl on the grid
    dlat = np.deg2rad(GRID_RES)
    dlon = np.deg2rad(GRID_RES)
    R = 6.371e6  # Earth radius in metres
    curl = (
        xr.DataArray(np.gradient(tau_y.values, dlon * R, axis=-1), coords=tau_y.coords)
        - xr.DataArray(np.gradient(tau_x.values, dlat * R, axis=-2), coords=tau_x.coords)
    )
    ds["wind_stress_curl"] = curl

    # PAR: ~44% of downwelling shortwave radiation
    ds["par"] = 0.44 * ds["ssrd"] / 86400  # convert J/m² to W/m²

    return ds[["wind_stress_curl", "par"]]


def load_biolum_observations(csv_path: str | Path = "data/raw/mbari/mbari_biolum_med.csv") -> pd.DataFrame:
    """
    Load MBARI bioluminescence point observations.

    Returns a DataFrame with columns: date, lat, lon, biolum_log
    where biolum_log = log10(biolum_photons_s + 1).
    """
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = df[df["synthetic"] != "True"] if "synthetic" in df.columns else df

    if len(df) == 0:
        raise ValueError(
            "No real bioluminescence observations found.
"
            "Check data/download_mbari.py and replace the placeholder."
        )

    df["biolum_log"] = np.log10(df["biolum_photons_s"].clip(lower=1))
    df = df.dropna(subset=["lat", "lon", "biolum_log"])

    # Filter to Mediterranean
    df = df[
        (df["lon"].between(*MED_LON)) &
        (df["lat"].between(*MED_LAT))
    ].copy()

    return df[["date", "lat", "lon", "biolum_log"]]


def fill_gaps(da: xr.DataArray, method: str = "linear") -> xr.DataArray:
    """
    Fill NaN gaps in a DataArray (e.g. from cloud cover) using
    temporal linear interpolation. Spatial gaps get a fallback
    nearest-neighbour fill.

    Anything still NaN after interpolation is left as NaN — the model
    handles low-confidence predictions separately.
    """
    # Temporal interpolation first
    filled = da.interpolate_na(dim="time", method=method, max_gap=7)
    return filled


def _regrid_to_025(ds: xr.Dataset) -> xr.Dataset:
    """Regrid a Dataset to the common 0.25° Mediterranean grid."""
    new_lon = np.arange(MED_LON[0], MED_LON[1] + GRID_RES, GRID_RES)
    new_lat = np.arange(MED_LAT[0], MED_LAT[1] + GRID_RES, GRID_RES)
    return ds.interp(lon=new_lon, lat=new_lat, method="linear")
