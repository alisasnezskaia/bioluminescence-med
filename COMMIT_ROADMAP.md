# Commit Roadmap

Follow this over ~5 weeks. Spread commits across working days.
Don't do everything in one push. Real projects have gaps, fixes, and second thoughts.

---

## Week 1 — Setup and first data look

**Day 1**
- `initial commit: project scaffold and README`

**Day 2**
- `add CMEMS and ERA5 download scripts`

**Day 3**
- `add notebook 01: first look at Mediterranean SST and CHL`
  — just load the data and make a map. leave a note about the Ligurian gap issue.

**Day 4**
- `01_eda: add seasonal decomposition and anomaly overlays`

**Day 5**
- `01_eda: annotate 2018 and 2022 anomaly years on the time series`
  — write what you actually noticed when you looked at the plots.

---

## Week 2 — Feature engineering

**Day 8**
- `add notebook 02: feature engineering skeleton`

**Day 9**
- `02_features: add SST anomaly vs climatology and upwelling index`

**Day 10**
- `02_features: PAR x CHL interaction — had to check three papers to get this right`
  — this commit message alone tells a story. use it.

**Day 11**
- `add src/features.py — refactored from notebook`
  — extract reusable code only after you've been copy-pasting it twice.

**Day 12**
- `02_features: correlation matrix and mutual information with biolum labels`

---

## Week 3 — Probability model

**Day 15**
- `add notebook 03: XGBoost baseline - first attempt`

**Day 16**
- `03_model: first results look suspiciously good - switching to spatial CV`
  — this is the most important commit in the repo. write it honestly.

**Day 17**
- `add src/spatial_cv.py - block cross-validation splits`

**Day 18**
- `03_model: spatial CV results - MAE dropped 15% vs random split`
  — real numbers, even if they hurt.

**Day 19**
- `03_model: SHAP analysis - PAR x CHL is top feature, not SST anomaly`
  — write a markdown cell about why this makes physical sense.

---

## Week 4 — Anomaly detection

**Day 22**
- `add notebook 04: LSTM autoencoder - architecture draft`

**Day 23**
- `04_anomaly: first training run - loss not converging, checking batch norm`

**Day 24**
- `04_anomaly: switch to layer norm - now stable`

**Day 25**
- `04_anomaly: threshold calibration and bloom event catalogue`

**Day 26**
- `04_anomaly: autoencoder flagged 2018 Adriatic event - checking literature`
  — this is the moment. write it in the commit message.

---

## Week 5 — Atlas and validation

**Day 29**
- `add notebook 05: seasonal probability maps - cartopy setup`

**Day 30**
- `05_atlas: custom colormap - viridis washed out the structure`
  — honest. specific. shows you actually looked at the output.

**Day 31**
- `05_atlas: SHAP waterfall charts per bloom event`

**Day 33**
- `add notebook 06: literature validation against Cusack 2019 and Koprivnjak 2021`

**Day 34**
- `update README: results, what I learned, open questions`

---

## Notes

- Typo fix commits are good: `fix label in notebook 03`
- Rename commits are good: `rename utils.py to data_utils.py for clarity`
- Don't push on every day. Skip a Saturday or two.
- Never commit with message "update" or "changes"
- Write what you discovered, not just what you did
