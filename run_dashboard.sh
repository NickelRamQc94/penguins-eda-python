#!/usr/bin/env bash
# ==============================================================================
# Palmer Penguins — Automated Dashboard Launcher
# Author: Jean Carlos Rojas Herrera (RojasJeanDL)
# Description:
#     Self-contained launcher script that activates the virtual environment
#     and starts the Streamlit interactive dashboard automatically in browser.
# ==============================================================================

set -e

# Resolve absolute path of project directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "======================================================================"
echo " 🐧 Palmer Penguins — Launching Institutional AI & Analytics Dashboard"
echo "======================================================================"

# Activate virtual environment
if [ -f "$DIR/.venv/bin/activate" ]; then
    source "$DIR/.venv/bin/activate"
else
    echo "[ERROR] Virtual environment (.venv) not found. Please run:"
    echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Launch Streamlit dashboard and open browser automatically
exec streamlit run app.py
