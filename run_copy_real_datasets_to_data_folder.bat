@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Copy real datasets into Alboran Atlas data folders
echo ============================================================
echo.
echo This will copy AQUASAFE, GEBCO, ODYSSEA and glider files into:
echo data/aquasafe
echo data/bathymetry
echo data/odyssea
echo data/gliders
echo.
python copy_real_datasets_to_data_folder.py
pause
