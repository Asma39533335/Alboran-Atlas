@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Updating GitHub repository for Alboran Atlas v4
echo ============================================================
echo.
echo This script will commit local changes and try to push them.
echo If GitHub already has files, it will first pull with rebase.
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo Git is not installed or not in PATH.
    pause
    exit /b
)

git remote -v
echo.

git add .
git commit -m "Update Alboran Atlas v4 clean glider tracks" || echo No new local commit needed.

git pull --rebase origin main
if errorlevel 1 (
    echo.
    echo Pull/rebase failed, probably because of a conflict.
    echo If this repository is only for Alboran Atlas and you want to overwrite GitHub with this local version,
    echo run this command manually:
    echo.
    echo git push --force-with-lease origin main
    echo.
    pause
    exit /b
)

git push -u origin main
if errorlevel 1 (
    echo.
    echo Normal push failed. If you want this local version to replace the GitHub version, run:
    echo.
    echo git push --force-with-lease origin main
    echo.
    pause
    exit /b
)

echo.
echo Done. Refresh GitHub and Streamlit Cloud.
pause
