@echo off
echo ========================================
echo    BLSC Ultimate Web Browser Launcher
echo ========================================
echo.
echo Starting BLSC Ultimate Browser...
echo Features: Embedded web rendering, multiple tabs, bookmarks!
echo Websites render INSIDE the browser window!
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found! Starting Ultimate Browser...
echo.

REM Clean up any corrupted data files
if exist browser_data.json (
    echo Checking browser data file...
    python -c "import json; json.load(open('browser_data.json'))" 2>nul
    if errorlevel 1 (
        echo Fixing corrupted browser data...
        del browser_data.json
    )
)

echo Starting BLSC Ultimate Browser...
python ultimate_browser.py

REM If there's an error, show it
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Ultimate Browser
    echo.
    echo Trying simple browser...
    python browser.py
)

echo.
echo Browser closed.
pause