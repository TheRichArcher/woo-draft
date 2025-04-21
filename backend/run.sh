#!/bin/bash
set -e

# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000 