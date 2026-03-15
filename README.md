# bioluminescence-med

The Mediterranean glows at night and almost nobody is tracking it at scale.
This project builds a bioluminescence probability field from satellite proxies
— SST anomalies, chlorophyll-a, upwelling signals — trained on sparse ship
observations, then flags the bloom events that don't fit the seasonal pattern.

> **Open the visual README for the full project overview:**
> [`README_visual.html`](README_visual.html)
> *(download and open locally, or view via GitHub Pages)*

---

## The question

Can you predict where the ocean is likely glowing tonight using nothing
but satellite observables — and catch the events that don't fit the pattern?

Ground truth: MBARI ship logs + Copernicus biogeochemistry reanalysis

---

## Stack

- **Data**: CMEMS (SST, CHL, MLD, currents), ERA5 (wind, PAR), MBARI (observations)
- **Preprocessing**: xarray, cartopy, scipy
- **Model 1**: XGBoost with spatial block cross-validation
- **Model 2**: LSTM autoencoder for bloom anomaly detection
- **Explainability**: SHAP feature attribution
- **Visualisation**: cartopy, matplotlib with custom colormap

---

## Notebooks

| # | Notebook | What it covers |
|---|----------|----------------|
| 01 | `eda_mediterranean` | First look at CMEMS data, seasonal patterns, anomaly years |
| 02 | `feature_engineering` | SST anomaly, PAR×CHL interaction, upwelling index |
| 03 | `probability_model` | XGBoost training, spatial CV, SHAP analysis |
| 04 | `anomaly_detection` | LSTM autoencoder, bloom event catalogue |
| 05 | `visualisation_atlas` | Seasonal probability maps, bloom overlays |
| 06 | `validation_literature` | Cross-check against published Med bioluminescence papers |

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/bioluminescence-med.git
cd bioluminescence-med
pip install -r requirements.txt

# Needs free accounts at marine.copernicus.eu and cds.climate.copernicus.eu
# Add credentials to .env (see data/README.md)
python data/download_cmems.py
python data/download_era5.py
python data/download_mbari.py

jupyter lab notebooks/
```

---

## What I learned

Spatial block CV dropped my model scores by ~15% vs random splits.
That's the real number — the random split one was memorising autocorrelation.

PAR × CHL interaction turned out to be the most important feature,
not SST anomaly. The autoencoder flagged the 2018 Adriatic bloom before
I knew it existed — found a paper confirming it afterwards.

Full notes in `README_visual.html` and notebook 06.

---

## References

- Lapota et al. (1988) — Bioluminescence measurements, J. Exp. Mar. Biol. Ecol.
- Moline et al. (2009) — Bioluminescence in the sea, Oceanography
- Cusack et al. (2019) — Bioluminescence observations, Ligurian Sea
- Roberts et al. (2017) — Cross-validation strategies for spatial data, Ecography
