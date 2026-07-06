@echo off
echo Starting ResearchGPT Backend...
cd /d %~dp0
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r backend\requirements.txt
) else (
    call venv\Scripts\activate
)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
