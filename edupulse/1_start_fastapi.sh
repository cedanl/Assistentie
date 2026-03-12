#!/usr/bin/env bash
# Helper script to start the EduPulse FastAPI app using uv (Unix/Linux)

set -e

cd "$(dirname "$0")" # Ensure we're in the script's directory

# #########################################################################################
# THIS IS STRICTLY FORBIDDEN. TEMPORARILY STORED MY PERSONAL API KEY HERE FOR DEMO.
# DO NOT DISTRIBUTE!!!!!!
# export OPENAI_API_KEY=ASK ED
# #########################################################################################

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

# Install dependencies
echo "Installeren van dependencies..."
uv add -U -r requirements.txt

# If you want to enforce .env presence, uncomment and adapt these warnings/checks
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
echo "[START] Starting EduPulse FastAPI Server met uvicorn..."
echo
echo "Druk op Ctrl+C om de app te stoppen."
echo

uvicorn --host "127.0.0.1" --port 8000 backend.main:app --reload
RESULT=$?
if [ $RESULT -ne 0 ]; then
  echo
  echo "[FOUT] Er is een fout opgetreden bij het starten van de app."
fi
