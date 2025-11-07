@echo off
REM ====================================
REM Seruti Crawler - Auto Crawl Script
REM For Windows Task Scheduler
REM ====================================

echo ========================================
echo  Seruti BPS Crawler - Auto Mode
echo ========================================

REM Change to project directory
cd /d C:\Users\IPDS-OCID\crawlSeruti

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run auto crawl
python auto_crawl.py

echo.
echo Crawl completed
echo.
