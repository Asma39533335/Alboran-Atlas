@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Force-sync clean Alboran Atlas v5 to GitHub
echo ============================================================
echo.
echo Use this when your previous local Git folder has merge-conflict
echo markers such as <<<<<<< HEAD in app.py.
echo.
echo IMPORTANT:
echo Use this only if the GitHub repository is dedicated to Alboran Atlas.
echo It will replace the GitHub main branch with this clean local version.
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo Git is not installed or not in PATH.
    echo Install Git, then run this script again.
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
git commit -m "Clean Alboran Atlas v5 platform" || echo No new commit needed.

git branch -M main
git fetch origin main

echo.
echo Pushing clean v5 to GitHub...
git push --force-with-lease origin main

if errorlevel 1 (
    echo.
    echo Push failed. If this repo is ONLY for Alboran Atlas and you want to overwrite it,
    echo run this command manually:
    echo.
    echo git push --force origin main
    echo.
    pause
    exit /b
)

echo.
echo Done. Refresh GitHub. You should see app.py at the top level.
echo Then deploy on Streamlit Cloud:
echo Repository: Asma39533335/Alboran-Atlas
echo Branch: main
echo Main file path: app.py
pause
