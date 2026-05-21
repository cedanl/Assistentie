#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
uv run streamlit run frontend/app.py --server.port 8503
