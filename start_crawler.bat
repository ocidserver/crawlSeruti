@echo off
REM ====================================
REM Seruti Crawler - Auto Start Script
REM ====================================

echo ========================================
echo  Seruti BPS Crawler - Starting...
echo ========================================

REM Change to project directory
cd /d C:\Users\IPDS-OCID\crawlSeruti

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if activation successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Virtual environment activated
echo Starting Flask application...
echo.

REM Start the Flask app
python run.py

REM If Flask stops, show error
if errorlevel 1 (
    echo.
    echo ERROR: Flask application stopped with error
    pause
    exit /b 1
)
