
from pathlib import Path

from forecast_utils import MARINE_ZONES, fetch_openmeteo_forecast, save_forecast_cache, demo_forecast


def main():
    print("Alboran Atlas Forecast Desk — updating forecast cache")
    print("This connector tries live Open-Meteo marine/weather forecasts.")
    print("If live access fails, it creates demo forecast cache files so the platform remains usable.")
    print()

    ok = 0
    failed = 0
    for zone in MARINE_ZONES:
        print(f"Updating: {zone}")
        try:
            df = fetch_openmeteo_forecast(zone)
            p = save_forecast_cache(zone, df)
            print(f"  live forecast saved: {p}")
            ok += 1
        except Exception as e:
            print(f"  live forecast failed: {e}")
            print("  writing demo forecast fallback")
            df = demo_forecast(zone)
            p = save_forecast_cache(zone, df)
            print(f"  demo forecast saved: {p}")
            failed += 1

    print()
    print(f"Done. Live zones: {ok}; fallback/demo zones: {failed}")
    print("Forecast cache folder:", Path(__file__).resolve().parent / "forecast_cache")


if __name__ == "__main__":
    main()
