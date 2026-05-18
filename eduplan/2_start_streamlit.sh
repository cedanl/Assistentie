#!/usr/bin/env bash
# Helper script to start the EduPlan Streamlit frontend using uv (Unix/Linux)

# set -e

# cd "$(dirname "$0")" # Ensure we're in the script's directory
echo
echo
echo "##################################################################"
echo "#                                                                #"
echo "#             EduPlan Streamlit frontend                        #"
echo "#                                                                #"
echo "##################################################################"
echo


# Initialize uv project if not present
if [ ! -f "pyproject.toml" ]; then
  echo "Project EduPlan niet gevonden. Aanmaken..."
  uv init
  echo "Project EduPlan geinitialiseerd"
  echo "Virtual environment niet gevonden. Aanmaken..."
  uv venv
  echo "Virtual environment aangemaakt..."
fi

# Create virtual environment if not present
if [ ! -d ".venv" ]; then
  echo "Virtual environment niet gevonden. Aanmaken..."
  uv venv
  echo "Virtual environment aangemaakt..."
fi

# Activate virtual environment
echo "Activeren van de virtual environment"
source .venv/bin/activate
echo "Omgeving geactiveerd"

# Install dependencies
echo "Installeren van dependencies..."
uv sync

# Laad .env zodat ANTHROPIC_API_KEY (en andere env vars) beschikbaar zijn voor de frontend
set -a
[ -f .env ] && source .env
set +a

echo
echo "[START] Starting EduPlan Streamlit Server met uv..."
echo "[INFO] De app opent automatisch in je browser op http://localhost:8502 of http://localhost:8503"
echo
echo "Druk op Ctrl+C om de app te stoppen."
echo

# Try first port (8502)
uv run streamlit run --server.port 8502 frontend/app.py --server.headless false
RESULT=$?
if [ $RESULT -ne 0 ]; then
  echo
  echo "[BUSY] De Streamlit server is niet gestart. Port 8502 wordt waarschijlijk al gebruikt."
  echo "We proberen de Streamlit server te starten met port 8503."
  uv run streamlit run --server.port 8503 frontend/app.py --server.headless false
fi
