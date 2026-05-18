#!/usr/bin/env bash
# Helper script to start the EduPlan FastAPI app using uv (Unix/Linux)

set -e

# cd "$(dirname "$0")" # Ensure we're in the script's directory

echo
echo
echo "##################################################################"
echo "#                                                                #"
echo "#             EduPlan FastAPI backend                           #"
echo "#                                                                #"
echo "##################################################################"
echo


# Initialize uv project if not present
if [ ! -f "pyproject.toml" ]; then
  echo "Project EduPlan niet gevonden. Aanmaken..."
  uv init
  echo "Project EduPlan geinitialiseerd"
fi

# Create virtual environment if not present
if [ ! -d ".venv" ]; then
  echo "Virtual environment niet gevonden. Aanmaken..."
  uv venv
  echo "Virtual environment aangemaakt"
fi

# Activate virtual environment
echo "Activeren van de virtual environment"
source .venv/bin/activate
echo "Omgeving geactiveerd"

# Install dependencies
echo "Installeren van dependencies..."
uv sync

echo
echo "[START] Starting EduPlan FastAPI Server met uvicorn..."
echo
echo "Druk op Ctrl+C om de app te stoppen."
echo

# Laad .env zodat ANTHROPIC_API_KEY (en andere env vars) beschikbaar zijn voor de backend
set -a
[ -f .env ] && source .env
set +a

uvicorn --host "127.0.0.1" --port 8000 backend.main:app --reload
RESULT=$?
if [ $RESULT -ne 0 ]; then
  echo
  echo "[FOUT] Er is een fout opgetreden bij het starten van de app."
fi
