@echo off
REM Start the FastAPI backend on port 8567
cd /d "%~dp0"
C:\Users\10314\.local\bin\uv.exe run uvicorn app.main:app --host 0.0.0.0 --port 8567 --reload
pause
