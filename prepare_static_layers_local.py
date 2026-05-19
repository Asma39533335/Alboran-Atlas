
import json
from pathlib import Path, PureWindowsPath
import warnings

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ============================================================
# Prepare cloud-ready static layers for Alboran Atlas
#
# Run this script locally on your computer where the NetCDF files exist.
# It creates:
#   static_layers/*.png
#   static_layers/catalog.json
#
# Commit the static_layers folder to GitHub so Streamlit Cloud can show
# the data layers without needing access to your local C:\Users\... paths.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static_layers"
STATIC_DIR.mkdir(exist_ok=True)

DATA_DIR = Path(r"C:\Users\Asus\Desktop\aquasafe data")
REGIONAL_EXTENT = (-6.0, -1.5, 34.8, 37.0)
AQUASAFE_EXTENT = (-4.25, -2.05, 35.00, 35.72)

PATHS = {
    "aquasafe_ammonium": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-amonium-concentration.nc",
    "aquasafe_oxygen": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-dissolved-oxygen.nc",
    "aquasafe_u": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-Eastward Sea Water Velocity.nc",
    "aquasafe_v": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-flow-subset-06_14_2024_8_03_PM.nc",
    "aquasafe_ssh": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-flow-subset-ssh.nc",
    "aquasafe_phosphate": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-inorganic phosphate.nc",
    "aquasafe_nitrate": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-nitrate-concentration.nc",
    "aquasafe_phytoplankton": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-phytoplankton.nc",
    "aquasafe_salinity": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-sea-water-salinity.nc",
    "aquasafe_temperature": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-sea-water-temperature.nc",
    "aquasafe_zooplankton": r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-zooplankton.nc",
    "gebco": r"C:\Users\Asus\Desktop\bathymetry\gebco_alboran.nc",
    "m1_sst": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_L4_SST_REP_with_degC.nc",
    "m2_sst": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_L4_SST_REP_with_degC.nc",
    "m1_sss": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_PHY_REANALYSIS_SALINITY_0_500m_with_surface_and_0_50m_mean.nc",
    "m2_sss": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_PHY_REANALYSIS_SALINITY_0_500m_with_surface_and_0_50m_mean.nc",
}

LAYER_CATALOG = {
    "AQUASAFE temperature": dict(path_key="aquasafe_temperature", category="temperature", cmap="turbo", units="°C", source="AQUASAFE 16–26 May 2022"),
    "AQUASAFE salinity": dict(path_key="aquasafe_salinity", category="salinity", cmap="viridis", units="PSU", source="AQUASAFE 16–26 May 2022"),
    "AQUASAFE SSH": dict(path_key="aquasafe_ssh", category="ssh", cmap="RdBu_r", units="m", source="AQUASAFE 16–26 May 2022"),
    "AQUASAFE current speed": dict(path_key="current_speed", category="current_speed", cmap="plasma", units="m s⁻¹", source="AQUASAFE 16–26 May 2022"),
    "Dissolved oxygen": dict(path_key="aquasafe_oxygen", category="oxygen", cmap="YlGnBu", units="mg L⁻¹", source="AQUASAFE 16–26 May 2022"),
    "Nitrate": dict(path_key="aquasafe_nitrate", category="nitrate", cmap="magma_r", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Phosphate": dict(path_key="aquasafe_phosphate", category="phosphate", cmap="viridis", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Ammonium": dict(path_key="aquasafe_ammonium", category="ammonium", cmap="YlOrBr", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Phytoplankton": dict(path_key="aquasafe_phytoplankton", category="phytoplankton", cmap="YlGn", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Zooplankton": dict(path_key="aquasafe_zooplankton", category="zooplankton", cmap="PuBuGn", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Phyto:Zoo ratio": dict(path_key="phyto_zoo_ratio", category="ratio", cmap="magma", units="dimensionless", source="AQUASAFE 16–26 May 2022"),
    "Mission 1 SST": dict(path_key="m1_sst", category="temperature", cmap="turbo", units="°C", source="ODYSSEA / CMEMS"),
    "Mission 2 SST": dict(path_key="m2_sst", category="temperature", cmap="turbo", units="°C", source="ODYSSEA / CMEMS"),
    "Mission 1 surface salinity": dict(path_key="m1_sss", category="salinity", cmap="viridis", units="PSU", source="MED PHY reanalysis"),
    "Mission 2 surface salinity": dict(path_key="m2_sss", category="salinity", cmap="viridis", units="PSU", source="MED PHY reanalysis"),
    "GEBCO bathymetry": dict(path_key="gebco", category="bathymetry", cmap="Blues", units="m", source="GEBCO"),
}

SCALE_HINTS = {
    "oxygen": dict(vmin=7.50, vmax=7.80),
    "nitrate": dict(vmin=0.00, vmax=0.20),
    "phosphate": dict(vmin=0.03, vmax=0.06),
    "ammonium": dict(vmin=0.08, vmax=0.14),
    "phytoplankton": dict(vmin=1.0, vmax=4.0),
    "zooplankton": dict(vmin=0.15, vmax=0.55),
    "ratio": dict(vmin=2.0, vmax=12.0),
    "current_speed": dict(vmin=0.0, vmax=0.18),
    "bathymetry": dict(vmin=0.0, vmax=2500.0),
}

VARIABLE_CANDIDATES = {
    "temperature": ["analysed_sst_degC", "temperature", "thetao", "sea_water_temperature", "analysed_sst", "sst", "temp"],
    "salinity": ["so_surface", "surface_so", "so_0_50m_mean", "salinity_surface", "salinity", "sos", "so", "sea_water_salinity", "sss"],
    "ssh": ["ssh", "zos", "sea_surface_height", "surface_height", "sla", "adt"],
    "u": ["u", "uo", "eastward_sea_water_velocity", "eastward", "water_u", "ugos"],
    "v": ["v", "vo", "northward_sea_water_velocity", "northward", "water_v", "vgos"],
    "oxygen": ["dissolved_oxygen", "oxygen", "o2", "doxy"],
    "nitrate": ["nitrate", "no3"],
    "phosphate": ["inorganic_phosphorus", "phosphate", "po4"],
    "ammonium": ["ammonia", "ammonium", "amonium", "nh4"],
    "phytoplankton": ["phytoplankton", "phyto", "phyc", "chlorophyll", "chl"],
    "zooplankton": ["zooplankton", "zoo", "zooc"],
    "bathymetry": ["elevation", "z", "depth", "bathymetry"],
}


def windows_basename(path_like):
    raw = str(path_like)
    return PureWindowsPath(raw).name if ":" in raw or "\\" in raw else Path(raw).name


def find_file(path_like):
    p = Path(path_like)
    if p.exists():
        return p
    basename = windows_basename(path_like)
    candidates = [
        BASE_DIR / basename,
        BASE_DIR / "data" / basename,
        DATA_DIR / basename,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def detect_coord(ds, candidates):
    for name in candidates:
        if name in ds.coords:
            return name
        if name in ds.variables:
            return name
    lower = {str(k).lower(): k for k in list(ds.coords) + list(ds.variables)}
    for name in candidates:
        if name.lower() in lower:
            return lower[name.lower()]
    for k in list(ds.coords) + list(ds.variables):
        kl = str(k).lower()
        for name in candidates:
            if name.lower() in kl:
                return k
    return None


def detect_coords(ds):
    return {
        "lon": detect_coord(ds, ["lon", "longitude", "nav_lon", "x"]),
        "lat": detect_coord(ds, ["lat", "latitude", "nav_lat", "y"]),
        "time": detect_coord(ds, ["time", "time_counter", "t", "datetime", "valid_time"]),
        "depth": detect_coord(ds, ["depth", "deptht", "depthu", "depthv", "deptho", "lev", "level", "z", "olevel", "nav_lev"]),
    }


def normalize_longitudes(ds, lon_name):
    if lon_name is None or lon_name not in ds.variables:
        return ds
    lon = np.asarray(ds[lon_name].values, dtype=float)
    if np.nanmax(lon) > 180:
        lon_new = ((lon + 180) % 360) - 180
        ds = ds.assign_coords({lon_name: lon_new}).sortby(lon_name)
    return ds


def choose_variable(ds, category):
    candidates = VARIABLE_CANDIDATES.get(category, [])
    lower = {str(v).lower(): v for v in ds.data_vars}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    for dv in ds.data_vars:
        dvl = str(dv).lower()
        for cand in candidates:
            if cand.lower() in dvl:
                return dv
    if len(ds.data_vars) == 1:
        return list(ds.data_vars)[0]
    return list(ds.data_vars)[0]


def subset_extent(ds, lon_name, lat_name, extent):
    if lon_name is None or lat_name is None:
        return ds
    west, east, south, north = extent
    try:
        lon = ds[lon_name]
        lat = ds[lat_name]
        if lon.ndim == 1 and lat.ndim == 1:
            ds = ds.sel({lon_name: slice(west, east), lat_name: slice(south, north)})
    except Exception:
        pass
    return ds


def convert_units(arr, category):
    arr = np.asarray(arr, dtype=float)
    med = np.nanmedian(arr)
    if category == "temperature" and np.isfinite(med) and med > 100:
        arr = arr - 273.15
    if category == "salinity" and np.isfinite(med) and med < 1.0:
        arr = arr * 1000.0
    if category == "bathymetry":
        arr = np.where(arr < 0, -arr, np.nan)
    return arr


def reduce_surface_mean(path, category, extent):
    ds = xr.open_dataset(path)
    coords = detect_coords(ds)
    ds = normalize_longitudes(ds, coords["lon"])
    ds = subset_extent(ds, coords["lon"], coords["lat"], extent)
    coords = detect_coords(ds)

    if category == "bathymetry":
        var = choose_variable(ds, "bathymetry")
    else:
        var = choose_variable(ds, category)

    da = ds[var]
    depth_name = coords["depth"]
    if category != "bathymetry" and depth_name is not None and depth_name in da.dims:
        try:
            da = da.sel({depth_name: 0}, method="nearest")
        except Exception:
            da = da.isel({depth_name: 0})
    time_name = coords["time"]
    if time_name is not None and time_name in da.dims:
        da = da.mean(dim=time_name, skipna=True)
    da = da.squeeze()

    lon_name = coords["lon"]
    lat_name = coords["lat"]
    if lon_name in da.dims and lat_name in da.dims:
        try:
            da = da.transpose(lat_name, lon_name)
        except Exception:
            pass

    arr = convert_units(da.values, category)
    return xr.DataArray(arr, coords=da.coords, dims=da.dims, name=var), coords, var


def get_xy(da, coords):
    lon = da[coords["lon"]]
    lat = da[coords["lat"]]
    if lon.ndim == 1 and lat.ndim == 1:
        return np.meshgrid(lon.values, lat.values)
    if lon.ndim == 2 and lat.ndim == 2:
        return lon.values, lat.values
    return np.meshgrid(np.asarray(lon).squeeze(), np.asarray(lat).squeeze())


def layer_bounds(da, coords):
    X, Y = get_xy(da, coords)
    return [[float(np.nanmin(Y)), float(np.nanmin(X))], [float(np.nanmax(Y)), float(np.nanmax(X))]]


def robust_limits(arr, category):
    hint = SCALE_HINTS.get(category, {})
    if hint.get("vmin") is not None and hint.get("vmax") is not None:
        return hint["vmin"], hint["vmax"]
    vals = np.asarray(arr, dtype=float)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return 0.0, 1.0
    vmin = float(np.nanpercentile(vals, 2))
    vmax = float(np.nanpercentile(vals, 98))
    if category in ["temperature", "salinity"]:
        vmin = np.floor(vmin * 10) / 10
        vmax = np.ceil(vmax * 10) / 10
    if vmax <= vmin:
        vmax = vmin + 1
    return vmin, vmax


def save_layer_png(layer_name, da, coords, category, cmap):
    safe = "".join(ch if ch.isalnum() else "_" for ch in layer_name)
    image_file = f"{safe}.png"
    out = STATIC_DIR / image_file

    X, Y = get_xy(da, coords)
    Z = np.asarray(da.values, dtype=float)
    vmin, vmax = robust_limits(Z, category)

    fig = plt.figure(figsize=(8, 5), dpi=220)
    ax = plt.axes([0, 0, 1, 1])
    ax.axis("off")
    ax.contourf(X, Y, Z, levels=np.linspace(vmin, vmax, 24), cmap=cmap, vmin=vmin, vmax=vmax, extend="both")
    fig.savefig(out, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    return image_file, vmin, vmax, layer_bounds(da, coords)


def build_layer(layer_name, meta):
    pk = meta["path_key"]
    cat = meta["category"]

    if pk == "current_speed":
        up = find_file(PATHS["aquasafe_u"])
        vp = find_file(PATHS["aquasafe_v"])
        if up is None or vp is None:
            raise FileNotFoundError("Missing U/V velocity files")
        u, coords, _ = reduce_surface_mean(up, "u", AQUASAFE_EXTENT)
        v, _, _ = reduce_surface_mean(vp, "v", AQUASAFE_EXTENT)
        arr = np.sqrt(np.asarray(u.values)**2 + np.asarray(v.values)**2)
        da = xr.DataArray(arr, coords=u.coords, dims=u.dims, name="current_speed")
        return da, coords, "current_speed"

    if pk == "phyto_zoo_ratio":
        pp = find_file(PATHS["aquasafe_phytoplankton"])
        zp = find_file(PATHS["aquasafe_zooplankton"])
        if pp is None or zp is None:
            raise FileNotFoundError("Missing phyto/zoo files")
        p, coords, _ = reduce_surface_mean(pp, "phytoplankton", AQUASAFE_EXTENT)
        z, _, _ = reduce_surface_mean(zp, "zooplankton", AQUASAFE_EXTENT)
        arr = np.asarray(p.values) / np.where(np.asarray(z.values) > 0, np.asarray(z.values), np.nan)
        da = xr.DataArray(arr, coords=p.coords, dims=p.dims, name="phyto_zoo_ratio")
        return da, coords, "phyto_zoo_ratio"

    path = find_file(PATHS[pk])
    if path is None:
        raise FileNotFoundError(PATHS[pk])
    extent = AQUASAFE_EXTENT if pk.startswith("aquasafe") else REGIONAL_EXTENT
    if cat == "bathymetry":
        extent = REGIONAL_EXTENT
    return reduce_surface_mean(path, cat, extent)


def main():
    catalog = {}
    failed = []

    for layer_name, meta in LAYER_CATALOG.items():
        print(f"Processing {layer_name}...")
        try:
            da, coords, var = build_layer(layer_name, meta)
            image_file, vmin, vmax, bounds = save_layer_png(layer_name, da, coords, meta["category"], meta["cmap"])
            catalog[layer_name] = {
                "image_file": image_file,
                "bounds": bounds,
                "vmin": round(float(vmin), 6),
                "vmax": round(float(vmax), 6),
                "units": meta["units"],
                "source": meta["source"],
                "variable": str(var),
                "category": meta["category"],
            }
            print(f"  saved {image_file}")
        except Exception as e:
            failed.append({"layer": layer_name, "error": str(e)})
            print(f"  ERROR: {e}")

    with open(STATIC_DIR / "catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    if failed:
        with open(STATIC_DIR / "failed_layers.json", "w", encoding="utf-8") as f:
            json.dump(failed, f, indent=2)

    print()
    print(f"Static catalog written: {STATIC_DIR / 'catalog.json'}")
    print(f"Successful layers: {len(catalog)}")
    print(f"Failed layers: {len(failed)}")
    print()
    print("Next step:")
    print("git add static_layers")
    print('git commit -m "Add static DTO layers"')
    print("git push")


if __name__ == "__main__":
    main()
