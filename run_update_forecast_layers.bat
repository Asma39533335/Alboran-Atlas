@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Alboran Atlas Forecast Desk - update forecast layers
echo ============================================================
echo.
echo Installing/checking packages...
python -m pip install -r requirements.txt

echo.
python update_forecast_layers.py

echo.
echo If you want cached forecasts available online, push forecast_cache:
echo git add forecast_cache
echo git commit -m "Update forecast cache"
echo git push
pause
