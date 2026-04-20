#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
