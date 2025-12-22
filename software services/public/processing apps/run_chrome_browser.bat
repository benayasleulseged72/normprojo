@echo off
echo ========================================
echo    BLSC Chrome Web Browser Launcher
echo ========================================
echo.
echo Starting BLSC Chrome Browser...
echo This browser uses Chromium engine for REAL web browsing!
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

echo Python found! Installing required packages...
echo.

REM Install CEF Python for real web rendering
echo Installing CEF Python (this may take a moment)...
python -m pip install cefpython3 --quiet

if errorlevel 1 (
    echo.
    echo CEF installation failed, trying webview...
    python -m pip install pywebview --quiet
    
    if errorlevel 1 (
        echo.
        echo Could not install web rendering engine.
        echo Falling back to simple browser...
        python browser.py
        pause
        exit /b 1
    ) else (
        echo.
        echo Starting WebView browser...
        python real_browser.py
    )
) else (
    echo.
    echo Starting Chrome browser with full web support...
    python chrome_browser.py
)

REM If there's an error, show it
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start browser
    echo.
    echo Trying alternative browser...
    python real_browser.py
    
    if errorlevel 1 (
        echo.
        echo Falling back to simple browser...
        python browser.py
    )
)

echo.
echo Browser closed.
pause