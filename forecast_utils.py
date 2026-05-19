
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd

try:
    import requests
except Exception:
    requests = None


BASE_DIR = Path(__file__).resolve().parent
FORECAST_CACHE_DIR = BASE_DIR / "forecast_cache"
FORECAST_CACHE_DIR.mkdir(exist_ok=True)

MARINE_ZONES: Dict[str, Dict[str, float | str]] = {
    "Western Moroccan Alboran": {
        "lat": 35.55,
        "lon": -4.35,
        "description": "Western Alboran sector near Al Hoceima offshore approaches.",
    },
    "Al Hoceima coastal sector": {
        "lat": 35.25,
        "lon": -3.93,
        "description": "Nearshore Al Hoceima sector and adjacent glider deployment area.",
    },
    "Central Moroccan Alboran": {
        "lat": 35.55,
        "lon": -3.45,
        "description": "Central Moroccan Mediterranean shelf and slope.",
    },
    "Nador coastal sector": {
        "lat": 35.25,
        "lon": -2.90,
        "description": "Eastern Moroccan Mediterranean / Nador coastal sector.",
    },
    "Full DTO domain centre": {
        "lat": 35.45,
        "lon": -3.45,
        "description": "Representative centre of the Alboran Atlas DTO domain.",
    },
}

SEA_STATE_SCALE = [
    ("Calm", 0.0, 0.5, "#2ca25f"),
    ("Slight", 0.5, 1.25, "#99d594"),
    ("Moderate", 1.25, 2.5, "#fee08b"),
    ("Rough", 2.5, 4.0, "#fdae61"),
    ("Very rough", 4.0, 6.0, "#f46d43"),
    ("High / severe", 6.0, 999.0, "#d73027"),
]


def cache_path(zone_name: str) -> Path:
    safe = "".join(ch if ch.isalnum() else "_" for ch in zone_name)
    return FORECAST_CACHE_DIR / f"{safe}_forecast.json"


def classify_sea_state(hs: float) -> Tuple[str, str]:
    try:
        hs = float(hs)
    except Exception:
        return "Unknown", "#9e9e9e"
    for label, lo, hi, color in SEA_STATE_SCALE:
        if lo <= hs < hi:
            return label, color
    return "Unknown", "#9e9e9e"


def marine_risk_level(hs: float, wind_kmh: Optional[float] = None) -> Tuple[str, str, str]:
    label, _ = classify_sea_state(hs)
    wind_kmh = float(wind_kmh) if wind_kmh is not None and np.isfinite(wind_kmh) else 0.0
    if hs >= 4.0 or wind_kmh >= 55:
        return "High", "#d73027", "Avoid small-vessel operations; review official forecasts."
    if hs >= 2.5 or wind_kmh >= 40:
        return "Elevated", "#f46d43", "Rough conditions likely; caution required."
    if hs >= 1.25 or wind_kmh >= 25:
        return "Moderate", "#fdae61", "Moderate sea state; monitor changes."
    return "Low", "#2ca25f", "Generally calm to slight conditions."


def direction_to_cardinal(deg: Optional[float]) -> str:
    if deg is None or not np.isfinite(deg):
        return "—"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((float(deg) + 22.5) // 45) % 8
    return dirs[idx]


def _request_json(url: str, params: dict, timeout: int = 20) -> dict:
    if requests is None:
        raise RuntimeError("The requests package is not available.")
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_openmeteo_forecast(zone_name: str, forecast_days: int = 7) -> pd.DataFrame:
    if zone_name not in MARINE_ZONES:
        raise KeyError(f"Unknown zone: {zone_name}")

    zone = MARINE_ZONES[zone_name]
    lat, lon = float(zone["lat"]), float(zone["lon"])

    marine_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "wave_height",
            "wave_direction",
            "wave_period",
            "wind_wave_height",
            "wind_wave_direction",
            "wind_wave_period",
            "swell_wave_height",
            "swell_wave_direction",
            "swell_wave_period",
        ]),
        "forecast_days": forecast_days,
        "timezone": "auto",
    }

    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ]),
        "forecast_days": forecast_days,
        "timezone": "auto",
    }

    marine = _request_json("https://marine-api.open-meteo.com/v1/marine", marine_params)
    weather = _request_json("https://api.open-meteo.com/v1/forecast", weather_params)

    mdf = pd.DataFrame(marine.get("hourly", {}))
    wdf = pd.DataFrame(weather.get("hourly", {}))

    if mdf.empty:
        raise RuntimeError("Marine forecast response was empty.")

    mdf["time"] = pd.to_datetime(mdf["time"])
    if not wdf.empty:
        wdf["time"] = pd.to_datetime(wdf["time"])
        df = pd.merge(mdf, wdf, on="time", how="left")
    else:
        df = mdf

    df["zone"] = zone_name
    df["lat"] = lat
    df["lon"] = lon
    df["source"] = "Open-Meteo live forecast"
    return df


def demo_forecast(zone_name: str, hours: int = 168) -> pd.DataFrame:
    zone = MARINE_ZONES.get(zone_name, MARINE_ZONES["Full DTO domain centre"])
    start = pd.Timestamp.now().floor("h")
    times = pd.date_range(start, periods=hours, freq="1h")
    t = np.arange(hours)

    zone_factor = 0.25 + 0.08 * (abs(float(zone["lon"])) - 3.0)
    wave_height = 0.85 + zone_factor + 0.35 * np.sin(2 * np.pi * t / 54) + 0.18 * np.sin(2 * np.pi * t / 19)
    wave_height = np.clip(wave_height, 0.25, 2.4)

    wind_speed = 16 + 7 * np.sin(2 * np.pi * t / 48 + 0.8) + 4 * np.sin(2 * np.pi * t / 17)
    wind_speed = np.clip(wind_speed, 4, 42)

    df = pd.DataFrame({
        "time": times,
        "wave_height": wave_height,
        "wave_direction": (45 + 60 * np.sin(2 * np.pi * t / 72)) % 360,
        "wave_period": np.clip(4.8 + 1.2 * np.sin(2 * np.pi * t / 60), 3.0, 8.0),
        "wind_wave_height": wave_height * 0.62,
        "wind_wave_direction": (70 + 50 * np.sin(2 * np.pi * t / 36)) % 360,
        "wind_wave_period": np.clip(3.5 + 0.9 * np.sin(2 * np.pi * t / 40), 2.0, 6.5),
        "swell_wave_height": wave_height * 0.38,
        "swell_wave_direction": (20 + 35 * np.sin(2 * np.pi * t / 90)) % 360,
        "swell_wave_period": np.clip(6.0 + 1.5 * np.sin(2 * np.pi * t / 80), 4.0, 10.0),
        "wind_speed_10m": wind_speed,
        "wind_direction_10m": (80 + 80 * np.sin(2 * np.pi * t / 60 + 0.3)) % 360,
        "wind_gusts_10m": wind_speed + 6,
    })
    df["zone"] = zone_name
    df["lat"] = float(zone["lat"])
    df["lon"] = float(zone["lon"])
    df["source"] = "Demo synthetic forecast"
    return df


def save_forecast_cache(zone_name: str, df: pd.DataFrame) -> Path:
    p = cache_path(zone_name)
    serial = df.copy()
    serial["time"] = serial["time"].astype(str)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({
            "zone": zone_name,
            "generated_at": pd.Timestamp.now().isoformat(),
            "records": serial.to_dict(orient="records"),
        }, f, indent=2)
    return p


def load_forecast_cache(zone_name: str) -> Optional[pd.DataFrame]:
    p = cache_path(zone_name)
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data.get("records", []))
    if df.empty:
        return None
    df["time"] = pd.to_datetime(df["time"])
    return df


def get_forecast(zone_name: str, mode: str = "Auto") -> pd.DataFrame:
    if mode == "Demo":
        return demo_forecast(zone_name)
    if mode == "Cache":
        cached = load_forecast_cache(zone_name)
        return cached if cached is not None else demo_forecast(zone_name)
    if mode in ["Auto", "Live Open-Meteo"]:
        try:
            df = fetch_openmeteo_forecast(zone_name)
            save_forecast_cache(zone_name, df)
            return df
        except Exception:
            if mode == "Live Open-Meteo":
                return demo_forecast(zone_name)
            cached = load_forecast_cache(zone_name)
            return cached if cached is not None else demo_forecast(zone_name)
    return demo_forecast(zone_name)


def select_forecast_time(df: pd.DataFrame, requested_time) -> pd.Series:
    times = pd.to_datetime(df["time"])
    req = pd.Timestamp(requested_time)
    idx = (times - req).abs().idxmin()
    return df.loc[idx]


def zone_forecast_summary(row: pd.Series) -> dict:
    hs = float(row.get("wave_height", np.nan))
    period = float(row.get("wave_period", np.nan))
    wdir = float(row.get("wave_direction", np.nan))
    wind = float(row.get("wind_speed_10m", np.nan))
    wind_dir = float(row.get("wind_direction_10m", np.nan))
    state, state_color = classify_sea_state(hs)
    risk, risk_color, advice = marine_risk_level(hs, wind)

    return {
        "time": str(row.get("time")),
        "hs": hs,
        "period": period,
        "wave_direction": wdir,
        "wave_cardinal": direction_to_cardinal(wdir),
        "wind_speed": wind,
        "wind_direction": wind_dir,
        "wind_cardinal": direction_to_cardinal(wind_dir),
        "sea_state": state,
        "sea_state_color": state_color,
        "risk": risk,
        "risk_color": risk_color,
        "advice": advice,
        "source": row.get("source", ""),
    }


def what_if_adjustment(row: pd.Series, wind_factor: float = 1.0, wave_offset: float = 0.0) -> dict:
    hs = max(0, float(row.get("wave_height", np.nan)) + float(wave_offset))
    wind = float(row.get("wind_speed_10m", np.nan)) * float(wind_factor)
    state, _ = classify_sea_state(hs)
    risk, risk_color, advice = marine_risk_level(hs, wind)
    return {
        "adjusted_hs": hs,
        "adjusted_wind": wind,
        "sea_state": state,
        "risk": risk,
        "risk_color": risk_color,
        "advice": advice,
    }
