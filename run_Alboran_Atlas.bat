@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo ALBORAN ATLAS v2 - Moroccan Mediterranean DTO Observatory
echo ============================================================
echo.
echo Installing / checking Python packages...
python -m pip install -r requirements.txt

echo.
echo Starting Alboran Atlas...
echo Login:
echo   username: asma
echo   password: alboran2026
echo.
python -m streamlit run app.py

pause
