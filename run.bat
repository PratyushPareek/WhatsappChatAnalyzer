@echo off
echo ============================================
echo  WAChatAnalysis — Setup ^& Run
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Download it from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

:: Create venv if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Install dependencies
echo Installing dependencies...
venv\Scripts\python.exe -m pip install --quiet --upgrade pip
venv\Scripts\python.exe -m pip install --quiet -r requirements.txt

:: Create folders
if not exist "chats" mkdir chats
if not exist "output" mkdir output

:: Check for chat files
dir /b chats\*.txt >nul 2>&1
if errorlevel 1 (
    echo.
    echo No chat files found in chats\ folder.
    echo Export a WhatsApp chat as .txt and place it in the chats\ folder.
    echo Then run this script again.
    pause
    exit /b 0
)

:: Run analysis
echo.
echo Running analysis...
venv\Scripts\python.exe -m src.main

echo.
echo Done! Reports are in the output\ folder.
pause
