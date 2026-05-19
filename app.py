
import os
import io
import base64
import json
from pathlib import Path, PureWindowsPath
import warnings

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import streamlit as st
import folium
from folium import FeatureGroup
from folium.raster_layers import ImageOverlay
from folium.plugins import MiniMap, MeasureControl, Fullscreen
from streamlit_folium import st_folium
from forecast_utils import (
    MARINE_ZONES,
    SEA_STATE_SCALE,
    get_forecast,
    select_forecast_time,
    zone_forecast_summary,
    what_if_adjustment,
    save_forecast_cache,
    classify_sea_state,
    marine_risk_level,
)


warnings.filterwarnings("ignore", category=RuntimeWarning)

# ============================================================
# ALBORAN ATLAS — Moroccan Mediterranean Digital Twin Observatory
# MVP v2, professional UI.
#
# Default demo login:
#   username: asma
#   password: alboran2026
#
# For deployment on Streamlit Cloud:
# - push this folder to GitHub
# - add secrets in Streamlit Cloud:
#     [auth]
#     username = "asma"
#     password = "your_password"
# ============================================================

APP_NAME = "Alboran Atlas"
APP_SUBTITLE = "Moroccan Mediterranean Digital Twin Observatory"
APP_TAGLINE = "Glider observations · AQUASAFE / ODYSSEA · CMEMS layers · GEBCO bathymetry"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(r"C:\Users\Asus\Desktop\aquasafe data")
CACHE_DIR = BASE_DIR / "cache_layers"
CACHE_DIR.mkdir(exist_ok=True)

STATIC_LAYER_DIR = BASE_DIR / "static_layers"
STATIC_LAYER_CATALOG = STATIC_LAYER_DIR / "catalog.json"

LOGO_CANDIDATES = [
    Path(r"C:\Users\Asus\Downloads\Al Boran Atlas LOGO.png"),
    BASE_DIR / "assets" / "Al Boran Atlas LOGO.png",
    BASE_DIR / "assets" / "Al_Boran_Atlas_LOGO.png",
    BASE_DIR / "assets" / "logo.png",
]

SEAEXPLORER_LOGO_CANDIDATES = [
    Path(r"C:\Users\Asus\Downloads\SeaExplorer2-scaled-removebg-preview.png"),
    BASE_DIR / "assets" / "SeaExplorer2-scaled-removebg-preview.png",
    BASE_DIR / "assets" / "SeaExplorer2.png",
    BASE_DIR / "assets" / "seaexplorer.png",
]

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

    "glider_m1_pld": r"C:\Users\Asus\Downloads\SEA038.26.pld1.sub.all.csv",
    "glider_m1_gli": r"C:\Users\Asus\Downloads\SEA038.26.gli.sub.all.csv",
    "glider_m2_pld": r"C:\Users\Asus\Downloads\SEA038.32.pld1.sub.all.csv",
    "glider_m2_gli": r"C:\Users\Asus\Downloads\SEA038.32.gli.sub.all.csv",

    "gebco": r"C:\Users\Asus\Desktop\bathymetry\gebco_alboran.nc",

    "m1_sst": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_L4_SST_REP_with_degC.nc",
    "m1_sst_raw": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_L4_SST_REP.nc",
    "m1_sss": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_PHY_REANALYSIS_SALINITY_0_500m_with_surface_and_0_50m_mean.nc",
    "m1_sss_raw": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_PHY_REANALYSIS_SALINITY_0_500m.nc",
    "m2_sst": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_L4_SST_REP_with_degC.nc",
    "m2_sst_raw": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_L4_SST_REP.nc",
    "m2_sss": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_PHY_REANALYSIS_SALINITY_0_500m_with_surface_and_0_50m_mean.nc",
    "m2_sss_raw": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_PHY_REANALYSIS_SALINITY_0_500m.nc",
    "m2_sst_l3s": r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_ODYSSEA_L3S_SST_subset.nc",
}

LAYER_CATALOG = {
    "AQUASAFE temperature": dict(path_key="aquasafe_temperature", category="temperature", cmap="turbo", group="Physical", units="°C", source="AQUASAFE 16–26 May 2022"),
    "AQUASAFE salinity": dict(path_key="aquasafe_salinity", category="salinity", cmap="viridis", group="Physical", units="PSU", source="AQUASAFE 16–26 May 2022"),
    "AQUASAFE SSH": dict(path_key="aquasafe_ssh", category="ssh", cmap="RdBu_r", group="Physical", units="m", source="AQUASAFE 16–26 May 2022"),
    "AQUASAFE current speed": dict(path_key="current_speed", category="current_speed", cmap="plasma", group="Physical", units="m s⁻¹", source="AQUASAFE 16–26 May 2022"),

    "Dissolved oxygen": dict(path_key="aquasafe_oxygen", category="oxygen", cmap="YlGnBu", group="Biogeochemistry", units="mg L⁻¹", source="AQUASAFE 16–26 May 2022"),
    "Nitrate": dict(path_key="aquasafe_nitrate", category="nitrate", cmap="magma_r", group="Biogeochemistry", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Phosphate": dict(path_key="aquasafe_phosphate", category="phosphate", cmap="viridis", group="Biogeochemistry", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Ammonium": dict(path_key="aquasafe_ammonium", category="ammonium", cmap="YlOrBr", group="Biogeochemistry", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),

    "Phytoplankton": dict(path_key="aquasafe_phytoplankton", category="phytoplankton", cmap="YlGn", group="Ecosystem", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Zooplankton": dict(path_key="aquasafe_zooplankton", category="zooplankton", cmap="PuBuGn", group="Ecosystem", units="mmol m⁻³", source="AQUASAFE 16–26 May 2022"),
    "Phyto:Zoo ratio": dict(path_key="phyto_zoo_ratio", category="ratio", cmap="magma", group="Ecosystem", units="dimensionless", source="AQUASAFE 16–26 May 2022"),

    "Mission 1 SST": dict(path_key="m1_sst", category="temperature", cmap="turbo", group="Mission context", units="°C", source="ODYSSEA / CMEMS"),
    "Mission 2 SST": dict(path_key="m2_sst", category="temperature", cmap="turbo", group="Mission context", units="°C", source="ODYSSEA / CMEMS"),
    "Mission 1 surface salinity": dict(path_key="m1_sss", category="salinity", cmap="viridis", group="Mission context", units="PSU", source="MED PHY reanalysis"),
    "Mission 2 surface salinity": dict(path_key="m2_sss", category="salinity", cmap="viridis", group="Mission context", units="PSU", source="MED PHY reanalysis"),

    "GEBCO bathymetry": dict(path_key="gebco", category="bathymetry", cmap="Blues", group="Bathymetry", units="m", source="GEBCO"),
}

MISSION_WINDOWS = {
    "SEA038.26 Mission 1": ("2020-11-10 00:00:00", "2020-12-07 23:59:59"),
    "SEA038.32 Mission 2": ("2021-02-11 00:00:00", "2021-03-17 23:59:59"),
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

# ============================================================
# STREAMLIT STYLE
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {height: 0rem;}
    .main {background-color: #F5FAFE;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 100%;}
    .atlas-shell {
        border: 1px solid #d6e5ee;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 8px 28px rgba(5, 45, 65, 0.08);
        padding: 1.1rem;
        margin-bottom: 1rem;
    }
    .brand-row {
        background: linear-gradient(120deg, #062f45 0%, #0a6f88 55%, #10a4b8 100%);
        color: white;
        border-radius: 18px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 30px rgba(0, 66, 92, 0.18);
    }
    .brand-title {
        font-size: 2.0rem;
        font-weight: 850;
        margin-bottom: 0.08rem;
    }
    .brand-subtitle {
        font-size: 0.98rem;
        opacity: 0.92;
    }
    .panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #063b5c;
        margin-bottom: 0.6rem;
    }
    .right-card {
        border: 1px solid #d6e5ee;
        border-radius: 14px;
        background: #ffffff;
        padding: 0.9rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 4px 18px rgba(5, 45, 65, 0.06);
    }
    .small-muted {
        color: #567080;
        font-size: 0.84rem;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #d6e5ee;
        border-radius: 12px;
        padding: 0.6rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        border-bottom: 1px solid #cfe1ec;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.55rem 0.75rem;
        border-radius: 10px 10px 0 0;
        font-weight: 750;
    }
    .stTabs [aria-selected="true"] {
        background: #e9f6fb;
        color: #006e9c;
    }
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    
    .forecast-card {
        border-radius: 18px;
        padding: 1rem 1.1rem;
        background: linear-gradient(145deg, #ffffff 0%, #eff9fc 100%);
        border: 1px solid #cfe5ee;
        box-shadow: 0 10px 28px rgba(8, 52, 76, 0.08);
        min-height: 115px;
    }
    .forecast-label {
        color: #567080;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03rem;
    }
    .forecast-value {
        color: #05324a;
        font-size: 1.65rem;
        font-weight: 850;
        margin-top: 0.15rem;
    }
    .forecast-sub {
        color: #476878;
        font-size: 0.86rem;
        margin-top: 0.2rem;
    }
    .risk-badge {
        color: white;
        font-weight: 850;
        border-radius: 999px;
        padding: 0.35rem 0.75rem;
        display: inline-block;
        margin-top: 0.3rem;
    }
    .phase-card {
        border: 1px solid #d4e6ef;
        border-radius: 16px;
        padding: 1rem;
        background: white;
        box-shadow: 0 8px 20px rgba(5, 45, 65, 0.06);
        height: 100%;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# AUTH
# ============================================================

def get_secret(name, default):
    try:
        if "auth" in st.secrets and name in st.secrets["auth"]:
            return st.secrets["auth"][name]
    except Exception:
        pass
    return os.getenv(f"ALBORAN_{name.upper()}", default)

LOGIN_USER = get_secret("username", "asma")
LOGIN_PASSWORD = get_secret("password", "alboran2026")


def find_logo():
    for p in LOGO_CANDIDATES:
        if p.exists():
            return p
    return None


def find_seaexplorer_logo():
    for p in SEAEXPLORER_LOGO_CANDIDATES:
        if p.exists():
            return p
    return None


def login_screen():
    logo = find_logo()
    col1, col2, col3 = st.columns([1.05, 1.1, 1.05])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div class='atlas-shell'>", unsafe_allow_html=True)
        if logo:
            st.image(str(logo), use_container_width=True)
        else:
            st.markdown(
                """
                <div style='text-align:center; font-size:2rem; font-weight:850; color:#063b5c;'>
                🌊 Alboran Atlas
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(
            f"""
            <div style='text-align:center; color:#24566f; margin-top:0.4rem;'>
            {APP_SUBTITLE}<br>
            <span style='font-size:0.85rem;'>{APP_TAGLINE}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="asma")
            pwd = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Enter DTO platform", use_container_width=True)
            if submitted:
                if user == LOGIN_USER and pwd == LOGIN_PASSWORD:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
        st.caption("Prototype demo access. Default: username `asma`, password `alboran2026`.")
        st.markdown("</div>", unsafe_allow_html=True)


def require_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        login_screen()
        st.stop()


# ============================================================
# DATA FUNCTIONS
# ============================================================

def windows_basename(path_like):
    raw = str(path_like)
    return PureWindowsPath(raw).name if ":" in raw or "\\" in raw else Path(raw).name


def find_file(path_like):
    raw = str(path_like)
    basename = windows_basename(raw)
    candidates = [
        Path(raw),
        BASE_DIR / basename,
        BASE_DIR / "data" / basename,
        BASE_DIR / "data" / "aquasafe" / basename,
        BASE_DIR / "data" / "gliders" / basename,
        BASE_DIR / "data" / "bathymetry" / basename,
        BASE_DIR / "data" / "odyssea" / basename,
        DATA_DIR / basename,
    ]
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        candidates.extend([
            Path(userprofile) / "Downloads" / basename,
            Path(userprofile) / "Desktop" / basename,
            Path(userprofile) / "Desktop" / "aquasafe data" / basename,
            Path(userprofile) / "Desktop" / "ODYSSEA_SST_Glider_Missions" / basename,
            Path(userprofile) / "Desktop" / "bathymetry" / basename,
        ])
    for c in candidates:
        if c.exists():
            return c
    return None


@st.cache_resource(show_spinner=False)
def open_dataset_cached(path_str):
    try:
        return xr.open_dataset(path_str)
    except Exception:
        return xr.open_dataset(path_str, decode_times=False)


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
    try:
        lon = np.asarray(ds[lon_name].values, dtype=float)
    except Exception:
        return ds
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


def select_time_if_requested(da, time_name, time_mode="Mean", selected_date=None):
    """
    For real NetCDF datasets, allow either temporal mean or daily/nearest snapshot.
    """
    if time_name is None or time_name not in da.dims:
        return da

    if time_mode == "Daily snapshot" and selected_date is not None:
        try:
            target = pd.Timestamp(selected_date)
            return da.sel({time_name: target}, method="nearest")
        except Exception:
            try:
                return da.isel({time_name: 0})
            except Exception:
                return da

    return da.mean(dim=time_name, skipna=True)


def reduce_bathymetry_layer(path, extent=REGIONAL_EXTENT):
    """
    Load GEBCO bathymetry from:
      C:\\Users\\Asus\\Desktop\\bathymetry\\gebco_alboran.nc

    Converts GEBCO elevation to positive water depth in metres.
    Land is set to NaN so it remains transparent on the map.
    """
    ds = open_dataset_cached(str(path))
    coords = detect_coords(ds)
    ds = normalize_longitudes(ds, coords["lon"])
    ds = subset_extent(ds, coords["lon"], coords["lat"], extent)
    coords = detect_coords(ds)

    var = None
    for cand in ["elevation", "z", "depth", "bathymetry", "Band1"]:
        if cand in ds.data_vars:
            var = cand
            break
        if cand in ds.variables and cand not in [coords.get("lon"), coords.get("lat")]:
            var = cand
            break
    if var is None:
        for dv in ds.data_vars:
            var = dv
            break
    if var is None:
        raise KeyError("No bathymetry/elevation variable found in GEBCO file.")

    da = ds[var].squeeze()
    arr = np.asarray(da.values, dtype=float)

    if np.nanmin(arr) < 0:
        depth = np.where(arr < 0, -arr, np.nan)
    else:
        depth = np.where(arr > 0, arr, np.nan)

    da = xr.DataArray(depth, coords=da.coords, dims=da.dims, attrs=da.attrs, name="GEBCO_depth_m")

    lon_name = coords["lon"]
    lat_name = coords["lat"]
    if lon_name in da.dims and lat_name in da.dims:
        try:
            da = da.transpose(lat_name, lon_name)
        except Exception:
            pass

    return da, coords, "GEBCO_depth_m"


def reduce_surface_mean(path, category, extent=REGIONAL_EXTENT, time_mode="Mean", selected_date=None):
    if category == "bathymetry":
        return reduce_bathymetry_layer(path, extent)

    ds = open_dataset_cached(str(path))
    coords = detect_coords(ds)
    ds = normalize_longitudes(ds, coords["lon"])
    ds = subset_extent(ds, coords["lon"], coords["lat"], extent)
    coords = detect_coords(ds)

    var = choose_variable(ds, category)
    da = ds[var]

    depth_name = coords["depth"]
    if depth_name is not None and depth_name in da.dims:
        try:
            da = da.sel({depth_name: 0}, method="nearest")
        except Exception:
            try:
                da = da.isel({depth_name: 0})
            except Exception:
                pass

    time_name = coords["time"]
    da = select_time_if_requested(da, time_name, time_mode=time_mode, selected_date=selected_date)

    da = da.squeeze()

    lon_name = coords["lon"]
    lat_name = coords["lat"]
    if lon_name in da.dims and lat_name in da.dims:
        try:
            da = da.transpose(lat_name, lon_name)
        except Exception:
            pass

    arr = convert_units(da.values, category)
    return xr.DataArray(arr, coords=da.coords, dims=da.dims, attrs=da.attrs, name=var), coords, var


def get_xy_from_da(da, coords):
    lon_name = coords["lon"]
    lat_name = coords["lat"]
    lon = da[lon_name]
    lat = da[lat_name]
    if lon.ndim == 1 and lat.ndim == 1:
        return np.meshgrid(lon.values, lat.values)
    if lon.ndim == 2 and lat.ndim == 2:
        return lon.values, lat.values
    return np.meshgrid(np.asarray(lon).squeeze(), np.asarray(lat).squeeze())


def layer_bounds(da, coords):
    X, Y = get_xy_from_da(da, coords)
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
        vmax = vmin + 1.0
    return vmin, vmax


def make_overlay_png(da, coords, category, cmap, layer_name):
    X, Y = get_xy_from_da(da, coords)
    Z = np.asarray(da.values, dtype=float)
    vmin, vmax = robust_limits(Z, category)

    safe_name = "".join(ch if ch.isalnum() else "_" for ch in layer_name)
    out_png = CACHE_DIR / f"{safe_name}.png"

    fig = plt.figure(figsize=(8, 5), dpi=220)
    ax = plt.axes([0, 0, 1, 1])
    ax.axis("off")
    ax.contourf(X, Y, Z, levels=np.linspace(vmin, vmax, 24), cmap=cmap, vmin=vmin, vmax=vmax, extend="both")
    fig.savefig(out_png, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    with open(out_png, "rb") as f:
        uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    return uri, vmin, vmax, layer_bounds(da, coords)



@st.cache_data(show_spinner=False)
def load_static_catalog():
    """
    Static layer catalog is produced locally by:
      prepare_static_layers_local.py

    It lets the deployed online platform show data layers even when
    Streamlit Cloud cannot access local C:\\Users\\... NetCDF paths.
    """
    if not STATIC_LAYER_CATALOG.exists():
        return {}
    try:
        with open(STATIC_LAYER_CATALOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def static_layer_available(layer_name):
    catalog = load_static_catalog()
    if layer_name not in catalog:
        return False
    img = STATIC_LAYER_DIR / catalog[layer_name].get("image_file", "")
    return img.exists()


def static_layer_to_data_uri(layer_name):
    catalog = load_static_catalog()
    meta = catalog[layer_name]
    img_path = STATIC_LAYER_DIR / meta["image_file"]
    with open(img_path, "rb") as f:
        uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    return uri, meta

def load_grid_layer(layer_name, time_mode="Mean", selected_date=None):
    """
    Load a platform layer from real NetCDF/CSV data.

    For AQUASAFE time-series products, use:
    - time_mode = "Mean" for temporal mean,
    - time_mode = "Daily snapshot" with selected_date for a nearest-time snapshot.
    """
    meta = LAYER_CATALOG[layer_name]
    path_key = meta["path_key"]
    category = meta["category"]

    if path_key == "current_speed":
        u_path = find_file(PATHS["aquasafe_u"])
        v_path = find_file(PATHS["aquasafe_v"])
        if u_path is None or v_path is None:
            raise FileNotFoundError("Current speed requires both U and V files.")
        u_da, u_coords, _ = reduce_surface_mean(u_path, "u", AQUASAFE_EXTENT, time_mode=time_mode, selected_date=selected_date)
        v_da, _, _ = reduce_surface_mean(v_path, "v", AQUASAFE_EXTENT, time_mode=time_mode, selected_date=selected_date)
        speed = np.sqrt(np.asarray(u_da.values, dtype=float) ** 2 + np.asarray(v_da.values, dtype=float) ** 2)
        return xr.DataArray(speed, coords=u_da.coords, dims=u_da.dims, name="current_speed"), u_coords, "current_speed"

    if path_key == "phyto_zoo_ratio":
        p_path = find_file(PATHS["aquasafe_phytoplankton"])
        z_path = find_file(PATHS["aquasafe_zooplankton"])
        if p_path is None or z_path is None:
            raise FileNotFoundError("Ratio requires phytoplankton and zooplankton files.")
        p_da, p_coords, _ = reduce_surface_mean(p_path, "phytoplankton", AQUASAFE_EXTENT, time_mode=time_mode, selected_date=selected_date)
        z_da, _, _ = reduce_surface_mean(z_path, "zooplankton", AQUASAFE_EXTENT, time_mode=time_mode, selected_date=selected_date)
        ratio = np.asarray(p_da.values, dtype=float) / np.where(np.asarray(z_da.values, dtype=float) > 0, np.asarray(z_da.values, dtype=float), np.nan)
        return xr.DataArray(ratio, coords=p_da.coords, dims=p_da.dims, name="phyto_zoo_ratio"), p_coords, "phyto_zoo_ratio"

    path = find_file(PATHS[path_key])
    if path is None:
        raise FileNotFoundError(f"Missing local/repository file: {PATHS[path_key]}")

    extent = AQUASAFE_EXTENT if path_key.startswith("aquasafe") else REGIONAL_EXTENT
    return reduce_surface_mean(path, category, extent, time_mode=time_mode, selected_date=selected_date)


# ============================================================
# GLIDER FUNCTIONS
# ============================================================

def coord_to_decimal(values, coord_type):
    """
    Convert SEA038 ALSEAMAR coordinates to decimal degrees.

    The uploaded files use DDMM.mmm formatting:
      Lat = 3514.155  -> 35°14.155' -> 35.2359
      Lon = -359.081  -> -3°59.081' -> -3.9847

    Already-decimal coordinates are preserved.
    """
    arr = pd.to_numeric(pd.Series(values), errors="coerce").to_numpy(dtype=float)
    out = arr.copy()
    absval = np.abs(arr)

    if coord_type == "lat":
        ddmm_mask = np.isfinite(arr) & (absval > 90)
    else:
        ddmm_mask = np.isfinite(arr) & (absval > 180)

    deg = np.floor(absval[ddmm_mask] / 100.0)
    minutes = absval[ddmm_mask] - deg * 100.0
    out[ddmm_mask] = np.sign(arr[ddmm_mask]) * (deg + minutes / 60.0)
    return out


def ddmm_to_decimal(values):
    arr = pd.to_numeric(pd.Series(values), errors="coerce").to_numpy(dtype=float)
    sign = np.sign(arr)
    absval = np.abs(arr)
    deg = np.floor(absval / 100.0)
    minutes = absval - deg * 100.0
    return sign * (deg + minutes / 60.0)


def parse_time(series):
    t = pd.to_datetime(series, format="%d/%m/%Y %H:%M:%S.%f", errors="coerce")
    if t.notna().sum() < 0.8 * len(series):
        t = pd.to_datetime(series, dayfirst=True, errors="coerce")
    return t


@st.cache_data(show_spinner=False)
def load_glider_csv(path_str):
    """
    Read either payload PLD files or navigation GLI files.

    PLD coordinates: NAV_LONGITUDE / NAV_LATITUDE
    GLI coordinates: Lon / Lat

    SEA038 coordinate format is DDMM.mmm, not plain decimal degrees.
    """
    df = pd.read_csv(path_str, sep=";", low_memory=False)
    df.columns = [str(c).strip().replace("\\ufeff", "") for c in df.columns]

    if "PLD_REALTIMECLOCK" in df.columns:
        df["time"] = parse_time(df["PLD_REALTIMECLOCK"])
    elif "Timestamp" in df.columns:
        df["time"] = parse_time(df["Timestamp"])
    else:
        df["time"] = pd.NaT

    if "NAV_LONGITUDE" in df.columns:
        df["lon"] = coord_to_decimal(df["NAV_LONGITUDE"], "lon")
    elif "Lon" in df.columns:
        df["lon"] = coord_to_decimal(df["Lon"], "lon")

    if "NAV_LATITUDE" in df.columns:
        df["lat"] = coord_to_decimal(df["NAV_LATITUDE"], "lat")
    elif "Lat" in df.columns:
        df["lat"] = coord_to_decimal(df["Lat"], "lat")

    if "NAV_DEPTH" in df.columns:
        df["depth_m"] = pd.to_numeric(df["NAV_DEPTH"], errors="coerce")
    elif "Depth" in df.columns:
        df["depth_m"] = pd.to_numeric(df["Depth"], errors="coerce")

    if "YO_NUMBER" in df.columns:
        df["YO_NUMBER"] = pd.to_numeric(df["YO_NUMBER"], errors="coerce")

    if "DeadReckoning" in df.columns:
        df["DeadReckoning"] = pd.to_numeric(df["DeadReckoning"], errors="coerce")

    return df


def haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0088
    lat1 = np.deg2rad(lat1)
    lon1 = np.deg2rad(lon1)
    lat2 = np.deg2rad(lat2)
    lon2 = np.deg2rad(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * radius_km * np.arcsin(np.sqrt(a))


def build_clean_glider_segments(df, mission_label=None, max_jump_km=18.0):
    """
    Clean mission track for map display.

    MVP v6 strategy:
    - strict mission-window filtering,
    - one representative near-surface position per YO cycle,
    - PLD cycle-median positions for full mission coverage,
    - split polylines at large navigation jumps,
    - remove zeros, 2018 test rows and out-of-domain coordinates.
    """
    if "lon" not in df.columns or "lat" not in df.columns:
        return []

    df = df.copy()

    if mission_label in MISSION_WINDOWS and "time" in df.columns and df["time"].notna().any():
        start, end = MISSION_WINDOWS[mission_label]
        df = df[(df["time"] >= pd.Timestamp(start)) & (df["time"] <= pd.Timestamp(end))].copy()

    mask = (
        np.isfinite(df["lon"])
        & np.isfinite(df["lat"])
        & df["lon"].between(REGIONAL_EXTENT[0], REGIONAL_EXTENT[1])
        & df["lat"].between(REGIONAL_EXTENT[2], REGIONAL_EXTENT[3])
    )
    df = df.loc[mask].copy()
    if len(df) < 2:
        return []

    rows = []
    if "YO_NUMBER" in df.columns and df["YO_NUMBER"].notna().sum() > 5:
        for yo, g in df.groupby("YO_NUMBER", sort=True):
            g = g.copy()
            if "time" in g.columns:
                g = g.sort_values("time")

            if "depth_m" in g.columns:
                cand = g[g["depth_m"].between(0, 12)]
                if len(cand) < 3:
                    cand = g[g["depth_m"].between(0, 50)]
                if len(cand) < 3:
                    cand = g
            else:
                cand = g

            if len(cand) < 1:
                continue

            row = {
                "YO_NUMBER": yo,
                "lon": float(cand["lon"].median()),
                "lat": float(cand["lat"].median()),
            }
            if "time" in g.columns and g["time"].notna().any():
                row["time"] = g["time"].min()
            rows.append(row)

        track = pd.DataFrame(rows)
        if len(track) < 2:
            return []
        if "time" in track.columns:
            track = track.sort_values("time")
        else:
            track = track.sort_values("YO_NUMBER")
    else:
        track = df[["lon", "lat"]].dropna()
        if "time" in df.columns:
            track["time"] = df.loc[track.index, "time"]
            track = track.sort_values("time")
        step = max(1, len(track) // 1200)
        track = track.iloc[::step].copy()

    lon = track["lon"].to_numpy(dtype=float)
    lat = track["lat"].to_numpy(dtype=float)

    keep = np.ones(len(lon), dtype=bool)
    keep[1:] = (np.abs(np.diff(lon)) > 1e-6) | (np.abs(np.diff(lat)) > 1e-6)
    lon, lat = lon[keep], lat[keep]
    if len(lon) < 2:
        return []

    jumps = haversine_km(lat[:-1], lon[:-1], lat[1:], lon[1:])
    split_indices = np.where(jumps > max_jump_km)[0] + 1
    lon_segments = np.split(lon, split_indices)
    lat_segments = np.split(lat, split_indices)

    segments = []
    for xs, ys in zip(lon_segments, lat_segments):
        if len(xs) >= 2:
            segments.append(list(zip(ys.astype(float), xs.astype(float))))
    return segments


def add_glider_track_to_map(fmap, label, path_key, color, show=True):
    path = find_file(PATHS[path_key])
    if path is None:
        return False
    try:
        df = load_glider_csv(str(path))
        segments = build_clean_glider_segments(df, mission_label=label)
        if not segments:
            return False

        fg = FeatureGroup(name=label, show=show)
        for seg in segments:
            folium.PolyLine(seg, color=color, weight=3, opacity=0.88, tooltip=label).add_to(fg)

        # Start/end markers use first and last valid segment.
        start = segments[0][0]
        end = segments[-1][-1]
        folium.CircleMarker(start, radius=6, color="black", fill=True, fill_color="lime", fill_opacity=1, tooltip=f"{label} start").add_to(fg)
        folium.CircleMarker(end, radius=6, color="black", fill=True, fill_color="cyan", fill_opacity=1, tooltip=f"{label} end").add_to(fg)

        fg.add_to(fmap)
        return True
    except Exception:
        return False


def conductivity_to_practical_salinity(C_s_per_m, T_degC, P_dbar):
    C = np.asarray(C_s_per_m, dtype=float) * 10.0
    T = np.asarray(T_degC, dtype=float)
    P = np.asarray(P_dbar, dtype=float)
    R = C / 42.914
    c0, c1, c2, c3, c4 = 0.6766097, 2.00564e-2, 1.104259e-4, -6.9698e-7, 1.0031e-9
    rT = c0 + c1*T + c2*T**2 + c3*T**3 + c4*T**4
    d1, d2, d3, d4 = 3.426e-2, 4.464e-4, 0.4215, -3.107e-3
    e1, e2, e3 = 2.070e-5, -6.370e-10, 3.989e-15
    Rp = 1 + (P * (e1 + e2*P + e3*P**2)) / (1 + d1*T + d2*T**2 + (d3 + d4*T)*R)
    RT = R / (rT * Rp)
    RT = np.where(RT > 0, RT, np.nan)
    x = np.sqrt(RT)
    a0, a1, a2, a3, a4, a5 = 0.0080, -0.1692, 25.3851, 14.0941, -7.0261, 2.7081
    b0, b1, b2, b3, b4, b5 = 0.0005, -0.0056, -0.0066, -0.0375, 0.0636, -0.0144
    k = 0.0162
    SP = a0 + a1*x + a2*RT + a3*RT*x + a4*RT**2 + a5*RT**2*x
    dS = ((T - 15) / (1 + k*(T - 15))) * (b0 + b1*x + b2*RT + b3*RT*x + b4*RT**2 + b5*RT**2*x)
    return np.where(SP + dS < 2, np.nan, SP + dS)


# ============================================================
# UI COMPONENTS
# ============================================================

def top_header():
    logo = find_logo()
    st.markdown("<div class='brand-row'>", unsafe_allow_html=True)
    cols = st.columns([0.10, 0.72, 0.18])
    with cols[0]:
        if logo:
            st.image(str(logo), use_container_width=True)
        else:
            st.markdown("<div style='font-size:2.0rem;'>🌊</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='brand-title'>{APP_NAME}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='brand-subtitle'>{APP_SUBTITLE}<br>{APP_TAGLINE}<br><b>Forecast Desk · DTO Insights · Scenario Lab</b></div>", unsafe_allow_html=True)
    with cols[2]:
        st.write("")
        if st.button("Log out", use_container_width=True):
            st.session_state["logged_in"] = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)



def map_dashboard():
    st.markdown("<div class='panel-title'>Operational map viewer</div>", unsafe_allow_html=True)

    left, right = st.columns([0.73, 0.27], gap="medium")

    with right:
        st.markdown("<div class='right-card'>", unsafe_allow_html=True)
        st.markdown("### 🌐 At sea")
        st.caption("Activate DTO layers")
        groups = ["Physical", "Biogeochemistry", "Ecosystem", "Mission context", "Bathymetry"]
        active_groups = st.multiselect(
            "Layer groups",
            groups,
            default=["Physical", "Biogeochemistry", "Ecosystem", "Mission context", "Bathymetry"],
        )
        layers = [name for name, meta in LAYER_CATALOG.items() if meta["group"] in active_groups]
        selected_layers = st.multiselect(
            "Visible layers",
            layers,
            default=[],
            placeholder="Choose one or more layers",
        )
        opacity = st.slider("Layer opacity", 0.2, 1.0, 0.72, 0.05)
        st.markdown("#### Time control")
        time_mode = st.radio("AQUASAFE fields", ["Mean", "Daily snapshot"], horizontal=True)
        selected_date = None
        if time_mode == "Daily snapshot":
            selected_date = st.date_input("Date", value=pd.Timestamp("2022-05-16"), min_value=pd.Timestamp("2022-05-16"), max_value=pd.Timestamp("2022-05-26"))
        st.caption("Real NetCDF layers can be shown as temporal mean or nearest daily snapshot.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='right-card'>", unsafe_allow_html=True)
        seaexplorer_logo = find_seaexplorer_logo()
        gl_col1, gl_col2 = st.columns([0.22, 0.78])
        with gl_col1:
            if seaexplorer_logo:
                st.image(str(seaexplorer_logo), use_container_width=True)
            else:
                st.markdown("<div style='font-size:1.8rem;'>🛥️</div>", unsafe_allow_html=True)
        with gl_col2:
            st.markdown("### SeaExplorer gliders")
            st.caption("Activate mission tracks when needed.")
        show_m1 = st.checkbox("SEA038.26 Mission 1", value=False)
        show_m2 = st.checkbox("SEA038.32 Mission 2", value=False)
        st.caption("Tracks use cleaned PLD cycle-median positions with DDMM.mmm → decimal conversion.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='right-card'>", unsafe_allow_html=True)
        st.markdown("### 🧭 Domain")
        zoom = st.slider("Initial zoom", 7, 11, 9)
        center_option = st.selectbox("Map center", ["Alboran / Moroccan Mediterranean", "Western Mediterranean", "Glider mission domain"])
        st.markdown("</div>", unsafe_allow_html=True)

    if center_option == "Western Mediterranean":
        center = [37.0, 2.0]
        zoom_start = 5
    elif center_option == "Glider mission domain":
        center = [35.55, -4.0]
        zoom_start = zoom
    else:
        center = [35.43, -3.25]
        zoom_start = zoom

    m = folium.Map(location=center, zoom_start=zoom_start, tiles="CartoDB positron")
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="Dark mode").add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    MeasureControl(position="topleft").add_to(m)
    Fullscreen(position="topleft").add_to(m)

    layer_summary = []
    unavailable_layers = []
    for layer_name in selected_layers:
        meta = LAYER_CATALOG[layer_name]
        try:
            # First try real local NetCDF/CSV data.
            da, coords, var = load_grid_layer(layer_name, time_mode=time_mode, selected_date=selected_date)
            uri, vmin, vmax, bounds = make_overlay_png(da, coords, meta["category"], meta["cmap"], layer_name)
            ImageOverlay(
                image=uri,
                bounds=bounds,
                name=f"{layer_name} ({meta['units']})",
                opacity=opacity,
                interactive=True,
                cross_origin=False,
                zindex=5,
            ).add_to(m)
            layer_summary.append((layer_name, meta["source"], var, f"{vmin:.3g}–{vmax:.3g}", meta["units"], "local NetCDF/CSV"))
        except Exception as local_error:
            # If deployed online, local C:\ paths are unavailable. Try precomputed static layers.
            if static_layer_available(layer_name):
                try:
                    uri, smeta = static_layer_to_data_uri(layer_name)
                    ImageOverlay(
                        image=uri,
                        bounds=smeta["bounds"],
                        name=f"{layer_name} ({smeta.get('units', meta['units'])})",
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=5,
                    ).add_to(m)
                    layer_summary.append((
                        layer_name,
                        smeta.get("source", meta["source"]),
                        smeta.get("variable", ""),
                        f"{smeta.get('vmin', '')}–{smeta.get('vmax', '')}",
                        smeta.get("units", meta["units"]),
                        "static cloud layer",
                    ))
                except Exception as static_error:
                    unavailable_layers.append((layer_name, f"static layer error: {static_error}"))
            else:
                unavailable_layers.append((layer_name, "local file missing and no static layer found"))

    if show_m1:
        add_glider_track_to_map(m, "SEA038.26 Mission 1", "glider_m1_pld", "#d73027", show=True)
    if show_m2:
        add_glider_track_to_map(m, "SEA038.32 Mission 2", "glider_m2_pld", "#1a9850", show=True)

    folium.LayerControl(collapsed=True).add_to(m)

    with left:
        st.markdown("<div class='atlas-shell'>", unsafe_allow_html=True)
        st_folium(m, width=None, height=720)
        st.markdown("</div>", unsafe_allow_html=True)

    if layer_summary:
        with st.expander("Active layer metadata", expanded=False):
            st.dataframe(
                pd.DataFrame(layer_summary, columns=["Layer", "Source", "Variable", "Scale", "Units", "Mode"]),
                use_container_width=True,
            )

    if unavailable_layers:
        with st.expander("Layers not shown", expanded=True):
            st.warning(
                "Some layers are not visible because Streamlit Cloud cannot access your local C:\\ files. "
                "Run `prepare_static_layers_local.py` on your computer, commit the generated `static_layers/` folder, "
                "and the online platform will display those layers."
            )
            st.dataframe(pd.DataFrame(unavailable_layers, columns=["Layer", "Reason"]), use_container_width=True)


def glider_explorer():
    st.markdown("<div class='panel-title'>Glider profile explorer</div>", unsafe_allow_html=True)
    mission = st.selectbox("Mission", ["SEA038.26 Mission 1", "SEA038.32 Mission 2"])
    path_key = "glider_m1_pld" if mission.startswith("SEA038.26") else "glider_m2_pld"
    path = find_file(PATHS[path_key])
    if path is None:
        st.error(f"Missing glider file: {PATHS[path_key]}")
        return

    df = load_glider_csv(str(path))
    if "YO_NUMBER" not in df.columns:
        st.error("YO_NUMBER column not found.")
        return

    cycles = sorted([int(v) for v in df["YO_NUMBER"].dropna().unique()])
    col1, col2 = st.columns([0.25, 0.75])
    with col1:
        yo = st.selectbox("YO cycle", cycles, index=min(10, len(cycles) - 1))
        st.metric("Available cycles", len(cycles))
        st.metric("Mission samples", f"{len(df):,}")
    with col2:
        g = df[df["YO_NUMBER"] == yo].copy()
        depth = pd.to_numeric(g.get("depth_m", np.nan), errors="coerce").to_numpy(dtype=float)
        temp = pd.to_numeric(g.get("GPCTD_TEMPERATURE", np.nan), errors="coerce").to_numpy(dtype=float)

        fig, ax = plt.subplots(1, 2, figsize=(9, 5), dpi=160)
        ax[0].plot(temp, depth, lw=1.4)
        ax[0].invert_yaxis()
        ax[0].set_xlabel("Temperature (°C)")
        ax[0].set_ylabel("Depth (m)")
        ax[0].grid(alpha=0.25)
        ax[0].set_title("Temperature profile")

        if all(c in g.columns for c in ["GPCTD_CONDUCTIVITY", "GPCTD_PRESSURE"]):
            C = pd.to_numeric(g["GPCTD_CONDUCTIVITY"], errors="coerce").to_numpy(dtype=float)
            P = pd.to_numeric(g["GPCTD_PRESSURE"], errors="coerce").to_numpy(dtype=float)
            S = conductivity_to_practical_salinity(C, temp, P)
            ax[1].plot(S, depth, lw=1.4)
            ax[1].invert_yaxis()
            ax[1].set_xlabel("Practical salinity (PSU)")
            ax[1].set_ylabel("Depth (m)")
            ax[1].grid(alpha=0.25)
            ax[1].set_title("Salinity profile")
        else:
            ax[1].axis("off")
            ax[1].text(0.5, 0.5, "Salinity inputs not found", ha="center", va="center")

        fig.suptitle(f"{mission} — YO cycle {yo}")
        st.pyplot(fig, use_container_width=True)


def data_catalog():
    st.markdown("<div class='panel-title'>Data catalog and online layer status</div>", unsafe_allow_html=True)
    rows = []
    for key, path in PATHS.items():
        found = find_file(path)
        rows.append({"Key": key, "Status": "available" if found else "missing", "Configured path": path, "Resolved path": str(found) if found else ""})
    df = pd.DataFrame(rows)

    static_catalog = load_static_catalog()
    static_count = sum(1 for lyr in LAYER_CATALOG if static_layer_available(lyr))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Configured files", len(df))
    c2.metric("Local files available", int((df["Status"] == "available").sum()))
    c3.metric("Static cloud layers", static_count)
    c4.metric("Platform layers", len(LAYER_CATALOG))

    st.markdown("### File availability")
    st.dataframe(df, use_container_width=True)

    st.markdown("### Static cloud-ready layers")
    if static_catalog:
        static_rows = []
        for name, meta in static_catalog.items():
            static_rows.append({
                "Layer": name,
                "Image": meta.get("image_file", ""),
                "Units": meta.get("units", ""),
                "Scale": f"{meta.get('vmin', '')}–{meta.get('vmax', '')}",
                "Source": meta.get("source", ""),
                "Exists": (STATIC_LAYER_DIR / meta.get("image_file", "")).exists(),
            })
        st.dataframe(pd.DataFrame(static_rows), use_container_width=True)
    else:
        st.info(
            "No `static_layers/catalog.json` found yet. "
            "For the online app, run `prepare_static_layers_local.py` locally and push the generated `static_layers/` folder to GitHub."
        )

    st.markdown("### Platform layer catalog")
    st.dataframe(pd.DataFrame([{"Layer": k, **v} for k, v in LAYER_CATALOG.items()]), use_container_width=True)

def glider_mission_summary(path_key, mission_label):
    path = find_file(PATHS[path_key])
    if path is None:
        return None
    try:
        df = load_glider_csv(str(path))
        if "YO_NUMBER" not in df.columns:
            return None
        return {
            "Mission": mission_label,
            "Samples": len(df),
            "Cycles": int(df["YO_NUMBER"].nunique()),
            "Start": str(df["time"].min()) if "time" in df and df["time"].notna().any() else "",
            "End": str(df["time"].max()) if "time" in df and df["time"].notna().any() else "",
            "Max depth (m)": float(pd.to_numeric(df.get("depth_m", np.nan), errors="coerce").max()),
        }
    except Exception:
        return None


def build_area_mean_timeseries(layer_name):
    """
    Build an area-mean time series from a real NetCDF layer.
    Works only when the NetCDF is available locally or packaged in data/.
    """
    meta = LAYER_CATALOG[layer_name]
    path_key = meta["path_key"]
    if path_key in ["current_speed", "phyto_zoo_ratio"]:
        return None

    path = find_file(PATHS[path_key])
    if path is None:
        return None

    try:
        ds = open_dataset_cached(str(path))
        coords = detect_coords(ds)
        ds = normalize_longitudes(ds, coords["lon"])
        extent = AQUASAFE_EXTENT if path_key.startswith("aquasafe") else REGIONAL_EXTENT
        ds = subset_extent(ds, coords["lon"], coords["lat"], extent)
        coords = detect_coords(ds)
        var = choose_variable(ds, meta["category"])
        da = ds[var]

        depth_name = coords["depth"]
        if depth_name is not None and depth_name in da.dims:
            try:
                da = da.sel({depth_name: 0}, method="nearest")
            except Exception:
                da = da.isel({depth_name: 0})

        time_name = coords["time"]
        if time_name is None or time_name not in da.dims:
            return None

        # Mean over every non-time dimension.
        dims_to_mean = [d for d in da.dims if d != time_name]
        ts = da.mean(dim=dims_to_mean, skipna=True)
        vals = convert_units(ts.values, meta["category"])
        times = pd.to_datetime(ds[time_name].values, errors="coerce")
        return pd.DataFrame({"time": times, "value": vals})
    except Exception:
        return None


def insights_dashboard():
    st.markdown("<div class='panel-title'>DTO insight dashboard</div>", unsafe_allow_html=True)

    static_count = sum(1 for lyr in LAYER_CATALOG if static_layer_available(lyr))
    local_count = sum(1 for p in PATHS.values() if find_file(p) is not None)
    packaged_count = 0
    for folder in [BASE_DIR / "data", BASE_DIR / "data" / "aquasafe", BASE_DIR / "data" / "gliders", BASE_DIR / "data" / "bathymetry", BASE_DIR / "data" / "odyssea"]:
        if folder.exists():
            packaged_count += len(list(folder.glob("*")))

    m1 = glider_mission_summary("glider_m1_pld", "SEA038.26 Mission 1")
    m2 = glider_mission_summary("glider_m2_pld", "SEA038.32 Mission 2")
    summaries = [s for s in [m1, m2] if s is not None]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Local/repository files", local_count)
    c2.metric("Packaged data files", packaged_count)
    c3.metric("Static online layers", static_count)
    c4.metric("Glider missions", len(summaries))

    st.markdown("### Glider mission summary")
    if summaries:
        sdf = pd.DataFrame(summaries)
        st.dataframe(sdf, use_container_width=True)

        cols = st.columns(2)
        for col, path_key, title, color in [
            (cols[0], "glider_m1_pld", "SEA038.26 depth sampling", "#d73027"),
            (cols[1], "glider_m2_pld", "SEA038.32 depth sampling", "#1a9850"),
        ]:
            path = find_file(PATHS[path_key])
            if path is not None:
                df = load_glider_csv(str(path))
                depth = pd.to_numeric(df.get("depth_m", np.nan), errors="coerce")
                depth = depth[np.isfinite(depth)]
                if len(depth) > 0:
                    fig, ax = plt.subplots(figsize=(6, 3.6), dpi=150)
                    ax.hist(depth, bins=45, color=color, alpha=0.78)
                    ax.set_xlabel("Depth (m)")
                    ax.set_ylabel("Sample count")
                    ax.set_title(title)
                    ax.grid(alpha=0.20)
                    col.pyplot(fig, use_container_width=True)
    else:
        st.info("No glider files are available yet. Add them to data/gliders or keep the configured local paths.")

    st.markdown("### AQUASAFE 2022 area-mean time series")
    ts_layers = [
        "AQUASAFE temperature",
        "AQUASAFE salinity",
        "Dissolved oxygen",
        "Nitrate",
        "Phosphate",
        "Ammonium",
        "Phytoplankton",
        "Zooplankton",
    ]
    selected_ts = st.multiselect("Choose variables", ts_layers, default=["AQUASAFE temperature", "Dissolved oxygen", "Phytoplankton"])
    if selected_ts:
        fig, ax = plt.subplots(figsize=(10, 4.8), dpi=160)
        plotted = 0
        for layer in selected_ts:
            ts = build_area_mean_timeseries(layer)
            if ts is None or ts["value"].dropna().empty:
                continue
            vals = ts["value"].to_numpy(dtype=float)
            # Normalize for multi-variable visual comparison.
            vals_norm = (vals - np.nanmin(vals)) / (np.nanmax(vals) - np.nanmin(vals) + 1e-12)
            ax.plot(ts["time"], vals_norm, marker="o", lw=2, label=layer)
            plotted += 1
        if plotted:
            ax.set_title("Normalized area-mean evolution, 16–26 May 2022")
            ax.set_ylabel("Normalized value")
            ax.set_xlabel("Time")
            ax.grid(alpha=0.25)
            ax.legend(loc="best", fontsize=8)
            st.pyplot(fig, use_container_width=True)
            st.caption("Normalized curves compare temporal patterns only. Use the Map tab for absolute values and units.")
        else:
            st.warning(
                "No real NetCDF time series is available to plot. "
                "To enable this online, copy AQUASAFE NetCDF files into data/aquasafe and push them to GitHub or use Git LFS/cloud storage."
            )

    st.markdown("### Online data strategy")
    st.info(
        "Best quality mode: put real NetCDF files in `data/aquasafe`, `data/bathymetry`, and `data/odyssea`. "
        "If GitHub size limits are a problem, use Git LFS or cloud-hosted NetCDF/Zarr. "
        "Static PNG layers are only a fallback for lightweight demos."
    )




def bearing_endpoint(lat, lon, bearing_deg, distance_km=35):
    # Simple approximate bearing endpoint for drawing arrows on a small map.
    radius = 6371.0088
    brng = np.deg2rad(bearing_deg)
    lat1 = np.deg2rad(lat)
    lon1 = np.deg2rad(lon)
    d = distance_km / radius
    lat2 = np.arcsin(np.sin(lat1) * np.cos(d) + np.cos(lat1) * np.sin(d) * np.cos(brng))
    lon2 = lon1 + np.arctan2(np.sin(brng) * np.sin(d) * np.cos(lat1), np.cos(d) - np.sin(lat1) * np.sin(lat2))
    return float(np.rad2deg(lat2)), float(np.rad2deg(lon2))


def forecast_card(label, value, sub=None, color=None):
    badge = ""
    if color:
        badge = f"<span class='risk-badge' style='background:{color};'>{value}</span>"
        value_html = badge
    else:
        value_html = f"<div class='forecast-value'>{value}</div>"
    sub_html = f"<div class='forecast-sub'>{sub}</div>" if sub else ""
    st.markdown(
        f"""
        <div class='forecast-card'>
            <div class='forecast-label'>{label}</div>
            {value_html}
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def forecast_desk():
    st.markdown("<div class='panel-title'>Forecast Desk — operational marine-state prototype</div>", unsafe_allow_html=True)

    st.info(
        "This module is a connector-ready forecast viewer. It can use live Open-Meteo marine/wind forecasts, "
        "cached forecasts, or a synthetic demo fallback. It is not yet an official operational warning system."
    )

    left, right = st.columns([0.70, 0.30], gap="medium")

    with right:
        st.markdown("<div class='right-card'>", unsafe_allow_html=True)
        st.markdown("### Forecast controls")
        zone_name = st.selectbox("Marine sector", list(MARINE_ZONES.keys()), index=1)
        mode = st.radio("Forecast source", ["Auto", "Live Open-Meteo", "Cache", "Demo"], index=0)
        lead = st.slider("Forecast lead time", 0, 168, 24, 3, help="Hours from the first forecast timestamp.")
        st.caption(MARINE_ZONES[zone_name]["description"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='right-card'>", unsafe_allow_html=True)
        st.markdown("### Scenario adjustment")
        wind_factor = st.slider("Wind multiplier", 0.5, 2.0, 1.0, 0.05)
        wave_offset = st.slider("Wave-height offset (m)", -0.8, 1.5, 0.0, 0.05)
        st.caption("This is a what-if sensitivity test, not a forecast correction.")
        st.markdown("</div>", unsafe_allow_html=True)

    df = get_forecast(zone_name, mode=mode)
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    selected_time = df["time"].iloc[0] + pd.Timedelta(hours=lead)
    row = select_forecast_time(df, selected_time)
    summary = zone_forecast_summary(row)
    adjusted = what_if_adjustment(row, wind_factor=wind_factor, wave_offset=wave_offset)

    with left:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            forecast_card("Sea state", summary["sea_state"], f"Hs = {summary['hs']:.2f} m", summary["sea_state_color"])
        with c2:
            forecast_card("Marine risk", summary["risk"], summary["advice"], summary["risk_color"])
        with c3:
            forecast_card("Wave period", f"{summary['period']:.1f} s", f"Direction {summary['wave_cardinal']} ({summary['wave_direction']:.0f}°)")
        with c4:
            forecast_card("Wind 10 m", f"{summary['wind_speed']:.1f} km/h", f"Direction {summary['wind_cardinal']} ({summary['wind_direction']:.0f}°)")

        st.markdown("#### Forecast map")
        fmap = folium.Map(location=[float(row["lat"]), float(row["lon"])], zoom_start=9, tiles="CartoDB positron")
        folium.TileLayer("CartoDB dark_matter", name="Dark mode").add_to(fmap)
        lat, lon = float(row["lat"]), float(row["lon"])

        # Zone marker.
        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color="black",
            weight=2,
            fill=True,
            fill_color=summary["risk_color"],
            fill_opacity=0.9,
            tooltip=f"{zone_name}: {summary['sea_state']} / {summary['risk']}",
        ).add_to(fmap)

        # Wave direction arrow.
        end_lat, end_lon = bearing_endpoint(lat, lon, summary["wave_direction"], distance_km=32)
        folium.PolyLine(
            [[lat, lon], [end_lat, end_lon]],
            color="#004b7a",
            weight=4,
            opacity=0.85,
            tooltip=f"Wave direction {summary['wave_direction']:.0f}°",
        ).add_to(fmap)

        # Domain reference.
        folium.Rectangle(
            bounds=[[35.00, -4.25], [35.72, -2.05]],
            color="#00A7C2",
            weight=2,
            fill=False,
            tooltip="AQUASAFE / Alboran Atlas DTO domain",
        ).add_to(fmap)

        folium.LayerControl(collapsed=True).add_to(fmap)
        st_folium(fmap, width=None, height=430)

        st.markdown("#### Forecast evolution")
        fig, ax1 = plt.subplots(figsize=(10, 4.4), dpi=160)
        ax1.plot(df["time"], df["wave_height"], lw=2.4, color="#006e9c", label="Significant wave height")
        ax1.scatter([row["time"]], [summary["hs"]], s=70, color=summary["risk_color"], edgecolor="black", zorder=5)
        ax1.set_ylabel("Wave height (m)")
        ax1.set_xlabel("Time")
        ax1.grid(alpha=0.25)

        ax2 = ax1.twinx()
        if "wind_speed_10m" in df.columns:
            ax2.plot(df["time"], df["wind_speed_10m"], lw=1.7, color="#f46d43", label="Wind speed 10 m", alpha=0.85)
            ax2.set_ylabel("Wind speed (km/h)")

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
        ax1.set_title(f"{zone_name} forecast — source: {summary['source']}")
        st.pyplot(fig, use_container_width=True)

        st.markdown("#### Scenario response")
        s1, s2, s3 = st.columns(3)
        with s1:
            forecast_card("Adjusted wave height", f"{adjusted['adjusted_hs']:.2f} m", "Hs after scenario offset")
        with s2:
            forecast_card("Adjusted wind", f"{adjusted['adjusted_wind']:.1f} km/h", "Wind after multiplier")
        with s3:
            forecast_card("Scenario risk", adjusted["risk"], adjusted["advice"], adjusted["risk_color"])

        with st.expander("Forecast data table", expanded=False):
            keep_cols = [c for c in [
                "time", "wave_height", "wave_period", "wave_direction",
                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
                "wind_wave_height", "swell_wave_height", "source"
            ] if c in df.columns]
            st.dataframe(df[keep_cols], use_container_width=True)

        st.caption(
            "Sea-state categories are based on significant wave height. "
            "This desk is designed as a DTO forecast-viewer prototype; official warnings should be issued by authorized agencies."
        )


def scenario_lab():
    st.markdown("<div class='panel-title'>Scenario & prototype prediction lab</div>", unsafe_allow_html=True)
    st.warning(
        "This is Phase 3 of the prototype: exploratory scenario intelligence. "
        "It is designed for decision-support prototyping, not official forecasting."
    )

    st.markdown(
        """
        <div class='phase-card'>
        <b>Three-phase concept</b><br>
        <b>Phase 1:</b> forecast viewer and marine-state cards.<br>
        <b>Phase 2:</b> live / cached data connectors.<br>
        <b>Phase 3:</b> scenario and prediction prototype using simple sensitivity rules.
        </div>
        """,
        unsafe_allow_html=True,
    )

    zone_name = st.selectbox("Scenario zone", list(MARINE_ZONES.keys()), index=1)
    df = get_forecast(zone_name, mode="Auto")
    df["time"] = pd.to_datetime(df["time"])
    row = select_forecast_time(df, df["time"].iloc[0] + pd.Timedelta(hours=24))

    st.markdown("### What-if marine-state scenario")
    col_a, col_b = st.columns(2)
    with col_a:
        wind_factor = st.slider("Wind forcing multiplier", 0.5, 2.5, 1.0, 0.05)
    with col_b:
        wave_offset = st.slider("Additional wave anomaly (m)", -1.0, 2.0, 0.0, 0.05)

    base = zone_forecast_summary(row)
    adj = what_if_adjustment(row, wind_factor=wind_factor, wave_offset=wave_offset)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        forecast_card("Base Hs", f"{base['hs']:.2f} m", base["sea_state"])
    with c2:
        forecast_card("Scenario Hs", f"{adj['adjusted_hs']:.2f} m", adj["sea_state"])
    with c3:
        forecast_card("Base risk", base["risk"], base["advice"], base["risk_color"])
    with c4:
        forecast_card("Scenario risk", adj["risk"], adj["advice"], adj["risk_color"])

    # Simple pseudo-probability response curve.
    hs_grid = np.linspace(0, max(4.0, adj["adjusted_hs"] + 1.0), 100)
    risk_score = 1 / (1 + np.exp(-(hs_grid - 1.8) * 2.2))
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160)
    ax.plot(hs_grid, risk_score, lw=2.5, color="#006e9c")
    ax.axvline(base["hs"], color="#2ca25f", lw=2, ls="--", label="Base")
    ax.axvline(adj["adjusted_hs"], color=adj["risk_color"], lw=2.5, ls="-", label="Scenario")
    ax.set_xlabel("Significant wave height (m)")
    ax.set_ylabel("Prototype risk score")
    ax.set_title("Scenario response curve")
    ax.grid(alpha=0.25)
    ax.legend()
    st.pyplot(fig, use_container_width=True)

    st.markdown("### Data-layer sensitivity map")
    layer = st.selectbox("Prototype environmental layer", ["AQUASAFE temperature", "AQUASAFE salinity", "Dissolved oxygen", "Phytoplankton"])
    offset = st.slider("Visual field offset", -2.0, 2.0, 0.0, 0.1)
    st.caption("This field offset is a visual sensitivity demonstration only.")

    try:
        da, coords, var = load_grid_layer(layer)
        da2 = da + offset
        X, Y = get_xy_from_da(da2, coords)
        fig, ax = plt.subplots(figsize=(9, 4.8), dpi=160)
        cf = ax.contourf(X, Y, da2.values, levels=24, cmap=LAYER_CATALOG[layer]["cmap"])
        ax.set_title(f"{layer} + visual offset {offset:+.1f}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        fig.colorbar(cf, ax=ax, label=LAYER_CATALOG[layer]["units"])
        st.pyplot(fig, use_container_width=True)
    except Exception as e:
        st.info(
            "Real environmental layer not available in this environment. "
            "Place NetCDF files in data/aquasafe or run the local copy script."
        )
        st.code(str(e))

def deployment_help():
    st.markdown("<div class='panel-title'>Deployment guide</div>", unsafe_allow_html=True)
    st.markdown(
        """
        Your screenshot says the app is **not connected to a remote GitHub repository**.  
        This package is now GitHub-ready, but the connection must be made on your computer/GitHub account.

        **Fast deployment workflow:**
        1. Put your platform logo in `assets/Al Boran Atlas LOGO.png`.
        2. Put your SeaExplorer logo in `assets/SeaExplorer2-scaled-removebg-preview.png`.
        3. Create a new GitHub repository.
        3. Push this folder to that repository.
        4. In Streamlit Community Cloud, choose the GitHub repo, branch, and `app.py`.
        5. Add secrets:
        ```toml
        [auth]
        username = "asma"
        password = "your_secure_password"
        ```

        **Important:** Streamlit Cloud cannot read `C:\\Users\\Asus\\...` local files.  
        For online deployment, use cloud-hosted NetCDF files, small demo data in the repo, or an OPeNDAP/THREDDS/CMEMS-access workflow.
        """
    )


def about_page():
    st.markdown("<div class='panel-title'>About Alboran Atlas</div>", unsafe_allow_html=True)
    st.markdown(
        """
        **Alboran Atlas** is a Moroccan Mediterranean Digital Twin Observatory prototype.

        It integrates:
        - SEA038 glider mission observations,
        - AQUASAFE / ODYSSEA surface-layer products,
        - CMEMS / reanalysis context layers,
        - GEBCO bathymetry,
        - physical, biogeochemical and ecosystem products.

        The current version is a **visualization and integration DTO prototype**.
        Future versions can add near-real-time ingestion, uncertainty layers, model comparison, and forecast/scenario modules.
        """
    )


# ============================================================
# MAIN
# ============================================================

require_login()
top_header()

tabs = st.tabs(["🗺️ Map", "🌦️ Forecast Desk", "🛥️ SeaExplorer", "📚 Data", "📊 Insights", "🧪 Scenarios", "ℹ️ About"])

with tabs[0]:
    map_dashboard()
with tabs[1]:
    forecast_desk()
with tabs[2]:
    glider_explorer()
with tabs[3]:
    data_catalog()
with tabs[4]:
    insights_dashboard()
with tabs[5]:
    scenario_lab()
with tabs[6]:
    about_page()
