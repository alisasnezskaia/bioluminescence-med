# Data

No raw data is committed to this repo. Run the download scripts to fetch everything.

## What you need

| Script | Source | Size (approx) | Notes |
|--------|--------|---------------|-------|
| `download_cmems.py` | CMEMS | ~4 GB | Free account required |
| `download_era5.py` | Copernicus CDS | ~1.5 GB | Free account required |
| `download_mbari.py` | MBARI | ~2 MB | Public, no auth needed |

## Credentials

CMEMS: register at marine.copernicus.eu, then add to `.env`:
```
CMEMS_USER=your_username
CMEMS_PASSWORD=your_password
```

ERA5 (CDS): register at cds.climate.copernicus.eu and follow the API setup guide.
This creates `~/.cdsapirc` automatically.

## Directory layout after download

```
data/raw/
├── cmems/
│   ├── sst/sst_2015-01-01_2023-12-31.nc
│   ├── chl/chl_2015-01-01_2023-12-31.nc
│   └── mld/mld_2015-01-01_2023-12-31.nc
├── era5/
│   ├── era5_med_2015.nc
│   └── ...
└── mbari/
    └── mbari_biolum_med.csv
```

## Bioluminescence observations

The MBARI dataset has sparse coverage in the Mediterranean — most observations
are from the Ligurian Sea and a few Adriatic transects. This sparsity is a real
constraint on the model, not something to paper over.

If you find additional Mediterranean bioluminescence datasets (there are some
in the PANGAEA data repository), the `src/data_utils.py` loader can be extended
to merge them.
