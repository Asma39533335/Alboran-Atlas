@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Preparing static cloud-ready layers for Alboran Atlas
echo ============================================================
echo.
echo This reads your local NetCDF files and creates static_layers/*.png
echo plus static_layers/catalog.json.
echo.
echo Installing/checking packages...
python -m pip install numpy pandas xarray matplotlib netCDF4 h5netcdf cftime

echo.
python prepare_static_layers_local.py

echo.
echo After this finishes, push static_layers to GitHub:
echo git add static_layers
echo git commit -m "Add static DTO layers"
echo git push
pause
