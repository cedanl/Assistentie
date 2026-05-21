#!/usr/bin/env bash
# Helper script to start the EduPlan FastAPI app using uv (Unix/Linux)

set -e

echo
echo "##################################################################"
echo "#                                                                #"
echo "#             EduPlan FastAPI backend                            #"
echo "#                                                                #"
echo "##################################################################"
echo

if [ ! -f "pyproject.toml" ]; then
  echo "[FOUT] pyproject.toml niet gevonden — draai dit script vanuit de eduplan/ map."
  exit 1
fi

echo "Installeren van dependencies..."
uv sync

# Laad .env zodat ANTHROPIC_API_KEY (en andere env vars) beschikbaar zijn voor de backend
set -a
[ -f .env ] && source .env
set +a

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo
  echo "[WAARSCHUWING] ANTHROPIC_API_KEY is niet gezet — LLM-endpoints (/summarize, /explain_risk, /map_columns) zullen falen."
  echo "Zet de key in .env of exporteer deze in je shell, en herstart het script."
  echo
fi

echo
echo "[START] Starting EduPlan FastAPI Server met uvicorn..."
echo "Druk op Ctrl+C om de app te stoppen."
echo

uv run uvicorn --host 127.0.0.1 --port 8000 backend.main:app --reload
