@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  where py >nul 2>nul && py -m venv .venv
  if not exist ".venv\Scripts\python.exe" where python >nul 2>nul && python -m venv .venv
  if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Python was not found. Install Python 3.10 or newer from https://www.python.org/downloads/
    echo During installation, select "Add Python to PATH", then run this file again.
    pause
    exit /b 1
  )
  echo Installing dependencies...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
if not exist "models\intent_classifier.joblib" (
  echo Training NLP model...
  ".venv\Scripts\python.exe" train.py
)
echo Opening CourseCompass at http://127.0.0.1:5000
start "" http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
pause
