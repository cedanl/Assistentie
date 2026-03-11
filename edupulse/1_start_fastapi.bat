@echo off
REM Helper script om de EduPulse app te starten met uv (Windows)

echo.
echo ========================================
echo   EduPulse - FASTAPI Starter Script
echo ========================================
echo.

cd /d "%~dp0"

if not exist "pyproject.toml" (
    echo uv project niet gevonden. Aanmaken...
    uv init
	uv venv	
)

REM Controleer of virtual environment bestaat
if not exist ".venv" (
    echo Virtual environment niet gevonden. Aanmaken...
    uv venv
)

REM Activeer virtual environment
call .venv\Scripts\activate

REM Installeer dependencies
echo Installeren van dependencies...
uv add -U -r requirements.txt

REM Check of .env bestand bestaat
REM if not exist .env (
REM     echo [WAARSCHUWING] .env bestand niet gevonden!
REM     echo.
REM     echo Kopieer .env.example naar .env en voeg je OpenAI API key toe:
REM     echo    copy .env.example .env
REM     echo.
REM     set /p continue="Wil je doorgaan zonder .env bestand? (j/n): "
REM     if /i not "%continue%"=="j" (
REM         if /i not "%continue%"=="ja" (
REM             echo.
REM             echo [GESTOPT] Maak eerst een .env bestand aan.
REM             pause
REM             exit /b 1
REM         )
REM     )
REM )

echo.
echo [START] Starting EduPulse FastAPI Server met uvicorn...
echo.
echo Druk op Ctrl+C om de app te stoppen.
echo.

# uvicorn backend.main:app --reload
uvicorn --host "127.0.0.1" --port 8000 backend.main:app --reload
if errorlevel 1 (
    echo.
    echo [FOUT] Er is een fout opgetreden bij het starten van de app.
)
