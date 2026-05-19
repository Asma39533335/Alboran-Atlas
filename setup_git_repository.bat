@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo GitHub setup for Alboran Atlas
echo ============================================================
echo.
echo This script initializes a Git repository and pushes to GitHub.
echo You must first create an empty repository on GitHub.
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo Git is not installed or not in PATH.
    echo Install Git from https://git-scm.com/ then run this script again.
    pause
    exit /b
)

git init
git add .
git commit -m "Initial Alboran Atlas DTO platform"
git branch -M main

set /p REPO_URL=Paste your GitHub repository URL here:
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo Done. Now deploy from Streamlit Community Cloud using:
echo Repository: %REPO_URL%
echo Branch: main
echo Main file path: app.py
pause
