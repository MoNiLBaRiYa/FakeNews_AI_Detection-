@echo off
REM Fake News Detection - Windows Startup Script

echo Starting Fake News Detection System...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration
    pause
    exit /b 1
)

REM Run the application
echo Starting Flask application...
python Backend\app.py

pause
