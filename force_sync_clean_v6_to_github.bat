@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Force-sync clean Alboran Atlas v6 to GitHub
echo ============================================================
echo.
echo Use this only if the GitHub repository is dedicated to Alboran Atlas.
echo It will replace the GitHub main branch with this clean local version.
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo Git is not installed or not in PATH.
    pause
    exit /b
)

git config --global user.name >nul 2>nul
if errorlevel 1 (
    set /p GITNAME=Enter your Git name, e.g. Asma:
    git config --global user.name "%GITNAME%"
)

git config --global user.email >nul 2>nul
if errorlevel 1 (
    set /p GITEMAIL=Enter your Git email:
    git config --global user.email "%GITEMAIL%"
)

git init
git remote remove origin 2>nul
git remote add origin https://github.com/Asma39533335/Alboran-Atlas.git

git add .
git commit -m "Clean Alboran Atlas v6 coordinates bathymetry" || echo No new commit needed.

git branch -M main
git fetch origin main
git push --force-with-lease origin main

if errorlevel 1 (
    echo.
    echo Push failed. If this repo is ONLY for Alboran Atlas and you want to overwrite it,
    echo run:
    echo git push --force origin main
    pause
    exit /b
)

echo.
echo Done. Refresh GitHub and Streamlit Cloud.
pause
