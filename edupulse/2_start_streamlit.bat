@echo off
REM Helper script om de EduPulse app te starten met uv (Windows)

echo.
echo ========================================
echo   EduPulse - Streamlit Starter Script
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
echo [START] Starting EduPulse Streamlit Server met uv...
echo [INFO] De app opent automatisch in je browser op http://localhost:8501 of http://localhost:8502
echo.
echo Druk op Ctrl+C om de app te stoppen.
echo.

uv run streamlit run frontend/app.py --server.headless false

if errorlevel 1 (
    echo.
    echo [FOUT] Er is een fout opgetreden bij het starten van de app.
	echo Waarschijlijk is de port 8501 bezet. We proberen port 8502.
	uv run streamlit run --server.port 8502 frontend/app.py --server.headless false
    
)
