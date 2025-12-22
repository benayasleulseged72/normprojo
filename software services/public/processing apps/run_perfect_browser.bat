@echo off
echo ========================================
echo    BLSC Perfect Web Browser Launcher
echo ========================================
echo.
echo Starting BLSC Perfect Browser...
echo Features: Multiple tabs, bookmarks, history, real web rendering!
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

echo Python found! Starting Perfect Browser...
echo.

REM Try to install webview for better web rendering
echo Installing web rendering engine (optional)...
python -m pip install pywebview --quiet >nul 2>&1

echo Starting BLSC Perfect Browser...
python perfect_browser.py

REM If there's an error, show it
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Perfect Browser
    echo.
    echo Trying fallback browser...
    python browser.py
)

echo.
echo Browser closed.
pause