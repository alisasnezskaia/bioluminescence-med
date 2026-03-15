"""
Proxy feature construction for bioluminescence prediction.

The idea: bioluminescence can't be observed directly from satellites,
but the conditions that trigger it can. Dinoflagellate bioluminescence
is a stress response — it correlates with photosynthetic stress
(PAR × CHL), thermal anomalies, and nutrient upwelling.

Features built here:
    sst_anomaly       departure from monthly climatology
    chl_log           log-transformed chlorophyll concentration
    par_x_chl         PAR × CHL interaction (photosynthetic stress proxy)
    upwelling_index   wind stress curl as Ekman upwelling proxy
    mld               mixed layer depth (stratification signal)
    chl_gradient      spatial gradient of CHL (bloom edge detection)
"""

import numpy as np
import xarray as xr


def build_features(cmems: xr.Dataset, era5: xr.Dataset) -> xr.Dataset:
    """
    Merge CMEMS and ERA5 into a feature Dataset.
    All variables are on the same 0.25° grid and daily time axis.

    Args:
        cmems: output of data_utils.load_cmems()
        era5:  output of data_utils.load_era5()

    Returns:
        xr.Dataset with one variable per feature
    """
    # Align time axes — ERA5 and CMEMS can have slight timestamp offsets
    era5 = era5.reindex(time=cmems.time, method="nearest", tolerance="12h")

    features = xr.Dataset()

    # SST anomaly (already computed in load_cmems)
    features["sst_anomaly"] = cmems["sst_anomaly"]

    # Log-transformed chlorophyll (heavy right tail otherwise)
    features["chl_log"] = np.log1p(cmems["chl"].clip(min=0))

    # PAR × CHL interaction — the most important feature empirically.
    # The intuition: high PAR + high CHL = photosynthetic stress = more bioluminescence.
    # Normalise each before multiplying to keep the scale sensible.
    par_norm = era5["par"] / era5["par"].mean()
    chl_norm = cmems["chl"] / cmems["chl"].mean()
    features["par_x_chl"] = par_norm * chl_norm

    # Upwelling index from wind stress curl
    # Positive curl (cyclonic) = upwelling = nutrient injection
    features["upwelling_index"] = era5["wind_stress_curl"]

    # Mixed layer depth — shallow MLD + high CHL often precedes blooms
    features["mld"] = cmems["mld"]

    # Spatial gradient of CHL — bloom edges are important
    # Use central differences on the lon/lat axes
    dchl_dlon = cmems["chl"].differentiate("lon")
    dchl_dlat = cmems["chl"].differentiate("lat")
    features["chl_gradient"] = np.sqrt(dchl_dlon**2 + dchl_dlat**2)

    # 7-day rolling mean of SST anomaly — captures persistence
    features["sst_anomaly_7d"] = (
        features["sst_anomaly"]
        .rolling(time=7, center=True, min_periods=3)
        .mean()
    )

    return features


def features_to_dataframe(features: xr.Dataset, obs: "pd.DataFrame") -> "pd.DataFrame":
    """
    Extract feature values at bioluminescence observation points.
    Used to build the training set for the XGBoost model.

    Args:
        features: xr.Dataset from build_features()
        obs:      DataFrame from data_utils.load_biolum_observations()

    Returns:
        DataFrame with one row per observation, feature columns + target column
    """
    import pandas as pd

    rows = []
    for _, row in obs.iterrows():
        try:
            cell = features.sel(
                time=row["date"],
                lat=row["lat"],
                lon=row["lon"],
                method="nearest",
            )
            feat_row = {var: float(cell[var].values) for var in features.data_vars}
            feat_row["biolum_log"] = row["biolum_log"]
            feat_row["date"] = row["date"]
            feat_row["lat"] = row["lat"]
            feat_row["lon"] = row["lon"]
            rows.append(feat_row)
        except Exception:
            continue

    return pd.DataFrame(rows)
