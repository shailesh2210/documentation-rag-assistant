@echo off
setlocal
py -3.14 --version
if errorlevel 1 (
  echo Python 3.14 was not found. Run: py --list
  exit /b 1
)
if not exist .venv py -3.14 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
echo.
echo Environment setup complete. Next run: python scripts\prepare_models.py
