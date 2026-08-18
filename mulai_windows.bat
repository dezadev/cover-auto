@echo off
setlocal
cd /d "%~dp0"
echo Menjalankan Cover Auto...
py -3 run_app.py
if errorlevel 1 (
  echo.
  echo Gagal memakai launcher py -3. Coba python run_app.py
  python run_app.py
)
pause
