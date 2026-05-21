#!/usr/bin/env bash
cd "$(dirname "$0")"

uv run --env-file .env uvicorn backend.main:app --host localhost --port 8001 --reload
