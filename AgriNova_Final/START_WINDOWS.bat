@echo off
title AgriNova Smart Agriculture Setup
cd /d "%~dp0"
echo ==========================================
echo       AgriNova Smart Agriculture
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python is not installed or not added to PATH.
  echo Install Python 3.10 or newer from python.org and tick "Add Python to PATH".
  pause
  exit /b 1
)
py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check your internet connection.
  pause
  exit /b 1
)
echo.
echo Setup complete. Starting AgriNova...
python app.py
pause
