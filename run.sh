#!/usr/bin/env bash
set -e

echo "============================================"
echo "  TECHCAMAI - Edge Camera Monitoring MVP"
echo "============================================"
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 not found. Install Python 3.10+ first."
    exit 1
fi

python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
echo
echo "[2/4] Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# Data directory
echo
echo "[3/4] Setting up data directory..."
mkdir -p data/clips

# Start server
echo
echo "[4/4] Starting TECHCAMAI..."
echo
echo "  Dashboard:  http://localhost:8000/"
echo "  API docs:   http://localhost:8000/docs"
echo "  Health:     http://localhost:8000/health"
echo
echo "  Press Ctrl+C to stop the server."
echo "============================================"
echo

export DB_PATH="$(pwd)/data/techcamai.db"
export CLIPS_DIR="$(pwd)/data/clips"

# Open browser (best-effort)
( sleep 2 && python3 -c "import webbrowser; webbrowser.open('http://localhost:8000/')" ) &

cd api
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
