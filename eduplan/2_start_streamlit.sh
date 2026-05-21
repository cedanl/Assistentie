#!/usr/bin/env bash
# Helper script to start the EduPlan Streamlit frontend using uv (Unix/Linux)

set -e

echo
echo "##################################################################"
echo "#                                                                #"
echo "#             EduPlan Streamlit frontend                         #"
echo "#                                                                #"
echo "##################################################################"
echo

if [ ! -f "pyproject.toml" ]; then
  echo "[FOUT] pyproject.toml niet gevonden — draai dit script vanuit de eduplan/ map."
  exit 1
fi

echo "Installeren van dependencies..."
uv sync

# Laad .env zodat env vars beschikbaar zijn voor de frontend
set -a
[ -f .env ] && source .env
set +a

echo
echo "[START] Starting EduPlan Streamlit Server met uv..."
echo "[INFO] De app opent automatisch in je browser op http://localhost:8502 of http://localhost:8503"
echo "Druk op Ctrl+C om de app te stoppen."
echo

if ! uv run streamlit run --server.port 8502 frontend/app.py --server.headless false; then
  echo
  echo "[BUSY] Port 8502 wordt waarschijnlijk al gebruikt — opnieuw proberen met port 8503."
  uv run streamlit run --server.port 8503 frontend/app.py --server.headless false
fi
