
# Alboran Atlas Forecast Desk — three-phase upgrade

This package adds the first operational-style forecast architecture to Alboran Atlas.

## Phase 1 — Forecast viewer

New tab:

```text
Forecast Desk
```

Features:
- Moroccan Mediterranean marine-sector selector
- forecast lead-time slider
- sea-state card
- wave height, wave period and wave direction
- 10 m wind card
- marine-risk indicator
- forecast map
- forecast time-series plot
- data table

## Phase 2 — Live / cached data connector

Connector script:

```text
update_forecast_layers.py
run_update_forecast_layers.bat
```

It tries to fetch live marine/wind forecasts from public Open-Meteo endpoints.
If live access fails, it creates a demo fallback cache so the platform remains usable.

Cache folder:

```text
forecast_cache
```

## Phase 3 — Scenario and prototype prediction lab

The Scenario tab now contains:
- wind forcing multiplier
- wave-height anomaly offset
- base vs scenario risk
- prototype risk-response curve
- environmental-layer sensitivity map

This is not an official operational forecast or warning product. It is a DTO prototype that can later be connected to validated operational products such as CMEMS, wave models, national meteorological services, or institutional forecast servers.

## Real datasets

The platform still supports real NetCDF datasets through:

```text
data/aquasafe
data/bathymetry
data/odyssea
data/gliders
```

Run:

```text
run_copy_real_datasets_to_data_folder.bat
```

to copy your local datasets into the project.

## Cloud deployment note

Streamlit Cloud cannot access local Windows paths such as:

```text
C:\Users\Asus\Desktop\aquasafe data
```

For online use:
1. put real datasets in `data/` and push them if file sizes allow,
2. use Git LFS for larger files,
3. or connect to external OPeNDAP/THREDDS/CMEMS/cloud-storage sources.
