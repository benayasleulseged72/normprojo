@echo off
echo ========================================
echo    BLSC Web Browser Launcher
echo ========================================
echo.
echo Starting BLSC Web Browser...
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

echo Python found! Starting browser...
echo.

REM Run the browser
python browser.py

REM If there's an error, show it
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start browser
    echo.
    echo Possible solutions:
    echo 1. Make sure Python is properly installed
    echo 2. Check if tkinter is available
    echo 3. Try running: pip install tk
    echo.
    pause
)

echo.
echo Browser closed.
pause