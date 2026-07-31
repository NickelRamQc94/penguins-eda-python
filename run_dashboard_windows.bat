@echo off
REM ==============================================================================
REM Palmer Penguins — Windows 10/11 Automated Dashboard Launcher (.BAT)
REM Author: Jean Carlos Rojas Herrera (RojasJeanDL)
REM Description:
REM     Double-click launcher for Windows 10 and Windows 11.
REM     Automatically checks/creates virtual environment, installs dependencies
REM     if missing, and opens the Streamlit Dashboard in the default web browser.
REM ==============================================================================

title Palmer Penguins AI & Analytics Dashboard - Launcher

echo ======================================================================
echo  Palmer Penguins - Launching Executive AI & Analytics Dashboard
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 was not found on your system.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo and ensure "Add Python to PATH" is checked during installation.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating .venv for Windows...
    python -m venv .venv
    echo [INFO] Installing required dependencies from requirements.txt...
    call .venv\Scripts\pip install -r requirements.txt
)

REM Activate environment and launch app
echo [SUCCESS] Starting Streamlit Dashboard in your browser...
call .venv\Scripts\activate.bat
streamlit run app.py
pause
