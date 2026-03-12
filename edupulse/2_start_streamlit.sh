#!/usr/bin/env bash
# Helper script to start the EduPulse Streamlit frontend using uv (Unix/Linux)

set -e

cd "$(dirname "$0")" # Ensure we're in the script's directory

# Initialize uv project if not present
if [ ! -f "pyproject.toml" ]; then
  echo "uv project niet gevonden. Aanmaken..."
  uv init
  uv venv
fi

# Create virtual environment if not present
if [ ! -d ".venv" ]; then
  echo "Virtual environment niet gevonden. Aanmaken..."
  uv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installeren van dependencies..."
uv add -U -r requirements.txt

# If you want to enforce .env presence, uncomment these warnings/checks
# if [ ! -f .env ]; then
#     echo "[WAARSCHUWING] .env bestand niet gevonden!"
#     echo
#     echo "Kopieer .env.example naar .env en voeg je OpenAI API key toe:"
#     echo "    cp .env.example .env"
#     echo
#     read -p "Wil je doorgaan zonder .env bestand? (j/n): " continue
#     if [[ ! "$continue" =~ ^[jJ]([aA])?$ ]]; then
#         echo
#         echo "[GESTOPT] Maak eerst een .env bestand aan."
#         exit 1
#     fi
# fi

echo
echo "[START] Starting EduPulse Streamlit Server met uv..."
echo "[INFO] De app opent automatisch in je browser op http://localhost:8501 of http://localhost:8502"
echo
echo "Druk op Ctrl+C om de app te stoppen."
echo

# Try first port (8501)
uv run streamlit run frontend/app.py --server.headless false
RESULT=$?
if [ $RESULT -ne 0 ]; then
  echo
  echo "[FOUT] Er is een fout opgetreden bij het starten van de app."
  echo "Waarschijnlijk is port 8501 bezet. We proberen port 8502."
  uv run streamlit run --server.port 8502 frontend/app.py --server.headless false
fi
