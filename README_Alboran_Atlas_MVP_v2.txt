# Alboran Atlas — Moroccan Mediterranean Digital Twin Observatory

## Default local login

```text
username: asma
password: alboran2026
```

## Run locally

Double-click:

```text
run_Alboran_Atlas.bat
```

## Logo

The app checks this local logo path:

```text
C:\Users\Asus\Downloads\Al Boran Atlas LOGO.png
```

For cloud deployment, copy the logo into:

```text
assets/Al Boran Atlas LOGO.png
```

## Modules

- Interactive map dashboard
- Right-side professional layer panel
- SEA038 glider tracks
- Glider YO-cycle profile viewer
- Data catalog / file availability checker
- Prototype scenario lab
- Deployment guide

## Important scientific framing

The AQUASAFE / ODYSSEA fields are May 2022 surface-layer DTO capability products.  
The SEA038 glider missions are from 2020–2021.  
Therefore, combined map views should be interpreted as integrated regional context / DTO capability views, not direct mission-time validation.

## Deploy

Read:

```text
README_DEPLOY_GITHUB_STREAMLIT.md
```


MVP v3 improvements
-------------------
- Initial map now opens cleanly with no gridded layers selected.
- SEA038 glider tracks are OFF by default and can be activated from the SeaExplorer panel.
- Glider tracks are cleaned using one median position per YO cycle and split at large navigation jumps.
  This removes artificial long lines caused by bad GPS fixes or track discontinuities.
- The right-side glider panel now supports the SeaExplorer logo:
  C:\Users\Asus\Downloads\SeaExplorer2-scaled-removebg-preview.png
- For cloud deployment, copy that logo into:
  assets/SeaExplorer2-scaled-removebg-preview.png


MVP v4 update
-------------
- Mission tracks now use the GLI navigation files for the map overlay:
  SEA038.26.gli.sub.all.csv
  SEA038.32.gli.sub.all.csv
- Mission tracks are filtered by strict mission windows.
- GLI tracks prefer real GPS fixes where DeadReckoning == 0 and shallow depth.
- Polylines are split at large navigation jumps to avoid artificial long lines.
- Map still opens with no gridded layers selected and glider tracks off by default.
- Added update_github_v4.bat to help solve GitHub push/rebase issues.


MVP v5 update
-------------
- Clean package without Git conflict markers.
- Includes force_sync_clean_v5_to_github.bat.
- Includes FIX_CONFLICT_AND_DEPLOY.md.
- Use v5 from a fresh extracted folder if your old Git folder contains `<<<<<<< HEAD` markers.


MVP v6 update
-------------
- Fixed SEA038 coordinate handling:
  * Lat example 3514.155 is converted to 35.2359 decimal degrees.
  * Lon example -359.081 is converted to -3.9847 decimal degrees.
  * Already-decimal coordinates are preserved.
- Map glider tracks use PLD cycle-median near-surface positions.
- Mission windows are applied before plotting tracks.
- Large jumps are split to avoid artificial long lines.
- GEBCO bathymetry layer explicitly uses:
  C:\Users\Asus\Desktop\bathymetry\gebco_alboran.nc
- GEBCO elevation is converted to positive water depth in metres.


MVP v7 update
-------------
- Removed the Deploy tab from the platform interface.
- Added a DTO Insight Dashboard with mission summaries and glider depth-distribution charts.
- Added packaged glider CSV fallback files in the `data/` folder, so the online app can display glider profiles/tracks.
- Added static cloud-ready layer support:
  * run `run_prepare_static_layers_local.bat` locally,
  * it creates `static_layers/*.png` and `static_layers/catalog.json`,
  * commit/push the `static_layers/` folder to GitHub,
  * Streamlit Cloud can then display AQUASAFE / ODYSSEA / GEBCO layers without local C:\ paths.
- The online app cannot access local `C:\Users\Asus\...` files directly; static layers solve this.


MVP v8 update
-------------
- Real NetCDF mode:
  Put AQUASAFE NetCDF files in `data/aquasafe`, GEBCO in `data/bathymetry`,
  and ODYSSEA/CMEMS mission products in `data/odyssea`.
- The deployed Streamlit app can then read real datasets directly instead of static PNGs.
- Added `run_copy_real_datasets_to_data_folder.bat` to copy your local datasets into those folders.
- Added AQUASAFE time control in the Map tab:
  * Mean
  * Daily snapshot
- Removed the Deploy tab from the interface.
- Added an improved DTO Insights dashboard with glider summaries and AQUASAFE area-mean time-series graphics.
- Static PNG layers remain as a lightweight fallback only.


MVP v9 update — Forecast Desk
-----------------------------
- Added Forecast Desk tab inspired by maritime forecast services.
- Added live/cached/demo marine forecast connector.
- Added sea-state cards, risk badges, forecast map and time-series graphics.
- Added `run_update_forecast_layers.bat`.
- Scenario Lab now includes a simple prototype prediction / what-if module.
- Real AQUASAFE NetCDF support from v8 is retained.
