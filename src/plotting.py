"""
Visualisation helpers for bioluminescence-med.

The main design decision here: matplotlib's standard colormaps
(viridis, plasma) don't work well for bioluminescence probability fields.
Viridis goes dark-to-light which reads as "deep ocean to shallow" not
"low probability to high probability". A custom dark-ocean-blue to
bioluminescence-teal ramp makes the spatial patterns readable at a glance.

Most functions return (fig, ax) so the caller can add titles, save, etc.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# Custom colormap: dark ocean blue → bioluminescence teal
# Built from two hex anchors so it's easy to tweak
_BIOLUM_COLORS = ["#04080f", "#0a2240", "#0d4f6b", "#0d8a7a", "#00c8b4", "#b2f0e8"]
BIOLUM_CMAP = mcolors.LinearSegmentedColormap.from_list("biolum", _BIOLUM_COLORS)

MED_EXTENT = [-6, 36.5, 30, 46]  # lon_min, lon_max, lat_min, lat_max


def med_map_ax(figsize=(12, 6)):
    """
    Return (fig, ax) with a Mediterranean basemap.
    Coastlines at 50m resolution, land filled gray.
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent(MED_EXTENT, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor="#1a1a2e", zorder=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, edgecolor="#4a6fa5", zorder=2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor="#2a3f5f", zorder=2)
    ax.gridlines(
        crs=ccrs.PlateCarree(),
        linewidth=0.3, color="gray", alpha=0.4,
        xlocs=range(-5, 37, 5), ylocs=range(31, 47, 3)
    )
    return fig, ax


def plot_probability_field(
    prob_field,     # xr.DataArray with dims (lat, lon)
    title: str = "",
    ax=None,
    vmin: float = 0.0,
    vmax: float = 1.0,
):
    """
    Plot a 2D bioluminescence probability field on a Mediterranean basemap.
    """
    if ax is None:
        fig, ax = med_map_ax()
    else:
        fig = ax.figure

    im = ax.pcolormesh(
        prob_field.lon, prob_field.lat, prob_field.values,
        transform=ccrs.PlateCarree(),
        cmap=BIOLUM_CMAP, vmin=vmin, vmax=vmax,
        shading="auto", zorder=0,
    )
    cb = plt.colorbar(im, ax=ax, orientation="vertical", pad=0.02, shrink=0.8)
    cb.set_label("P(bioluminescence)", fontsize=9, color="#7a9e96")
    cb.ax.yaxis.set_tick_params(color="#7a9e96", labelcolor="#7a9e96")
    if title:
        ax.set_title(title, fontsize=11, pad=8, color="#e8f4f0")

    return fig, ax


def plot_bloom_events(events: list[dict], scores: np.ndarray, dates, title: str = ""):
    """
    Timeline plot of anomaly scores with bloom events highlighted.
    """
    fig, ax = plt.subplots(figsize=(14, 4))
    fig.patch.set_facecolor("#04080f")
    ax.set_facecolor("#080f1c")

    ax.plot(dates, scores, color="#0d8a7a", lw=1.0, alpha=0.8, label="Anomaly score")

    threshold = np.nanpercentile(scores, 95)
    ax.axhline(threshold, color="#f5a623", lw=0.8, ls="--", alpha=0.6, label="95th pct threshold")

    for ev in events:
        ax.axvspan(ev["start"], ev["end"], alpha=0.25, color="#00c8b4", zorder=0)

    ax.set_xlabel("Date", color="#6a8e86", fontsize=9)
    ax.set_ylabel("Reconstruction MSE", color="#6a8e86", fontsize=9)
    ax.tick_params(colors="#6a8e86", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#1a2a3a")
    ax.legend(fontsize=8, facecolor="#080f1c", edgecolor="#1a2a3a", labelcolor="#e8f4f0")
    if title:
        ax.set_title(title, color="#e8f4f0", fontsize=11)

    plt.tight_layout()
    return fig, ax
