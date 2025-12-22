@echo off
echo ========================================
echo    BLSC Chrome-Like Browser Launcher
echo ========================================
echo.
echo Starting BLSC Chrome Browser...
echo Real Chromium rendering engine with full web compatibility!
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

echo Python found! Installing Chromium Embedded Framework...
echo This may take a few minutes on first run...
echo.

REM Install CEF Python for real Chrome rendering
python -m pip install cefpython3 --upgrade --quiet

if errorlevel 1 (
    echo.
    echo CEF installation failed. Browser will run in fallback mode.
    echo Websites will open in your default browser.
    echo.
) else (
    echo.
    echo CEF installed successfully! You now have real Chrome rendering!
    echo.
)

REM Clean up corrupted data
if exist browser_data.json (
    python -c "import json; json.load(open('browser_data.json'))" 2>nul
    if errorlevel 1 (
        echo Fixing browser data...
        del browser_data.json
    )
)

echo Starting BLSC Chrome Browser...
python chrome_like_browser.py

if errorlevel 1 (
    echo.
    echo Error starting Chrome browser. Trying fallback...
    python ultimate_browser.py
)

echo.
echo Browser closed.
pause