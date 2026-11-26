#!/bin/bash
# ==============================================================================
# Memora — run.sh
# Main launcher script for the Memora OS Resource-Management Simulator.
#
# Usage (from Git Bash / Linux / WSL):
#   bash bash/run.sh                 # Interactive launcher menu
#   bash bash/run.sh --demo-all      # Full 3-module Capstone Viva Demo
#   bash bash/run.sh --demo          # Virtual memory reference demo
#   bash bash/run.sh --module cpu    # Launch CPU scheduling directly
#   bash bash/run.sh --batch         # Run batch simulations
# ==============================================================================

set -e

# --- Detect project root ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "========================================================================"
echo "  Memora — Operating Systems Resource-Management Simulator"
echo "  Memory Management  |  CPU Scheduling  |  Deadlock Avoidance"
echo "========================================================================"
echo "  Project root: $PROJECT_ROOT"
echo ""

# --- Activate virtual environment ---
VENV_ACTIVATE="$PROJECT_ROOT/venv/Scripts/activate"
ALT_VENV_ACTIVATE="$PROJECT_ROOT/.venv/Scripts/activate"
LINUX_VENV="$PROJECT_ROOT/venv/bin/activate"

if [ -f "$VENV_ACTIVATE" ]; then
    echo "  Activating virtual environment (venv)..."
    source "$VENV_ACTIVATE"
elif [ -f "$ALT_VENV_ACTIVATE" ]; then
    echo "  Activating virtual environment (.venv)..."
    source "$ALT_VENV_ACTIVATE"
elif [ -f "$LINUX_VENV" ]; then
    echo "  Activating virtual environment (Linux/WSL)..."
    source "$LINUX_VENV"
else
    echo "  [NOTICE] Using system Python: $(python --version 2>&1)"
fi

cd "$PROJECT_ROOT"

# --- Argument Passthrough or Interactive Launcher ---
if [ $# -gt 0 ]; then
    echo "  Executing: python main.py $@"
    echo "========================================================================"
    python main.py "$@"
    exit 0
fi

echo "  Select execution mode:"
echo "    1) Interactive CLI (Full 3-Module Menu)"
echo "    2) Full Capstone Viva Demonstration (--demo-all)"
echo "    3) Start Web Dashboard (Flask Server on http://127.0.0.1:5000)"
echo "    4) Run Batch Memory Simulations (--batch)"
echo "    5) Run Comprehensive Test Suite (96 Unit Tests)"
echo "    6) Exit"
echo "========================================================================"
read -p "  Enter choice [1-6, default: 1]: " CHOICE

CHOICE=${CHOICE:-1}

case "$CHOICE" in
    1)
        python main.py
        ;;
    2)
        python main.py --demo-all
        ;;
    3)
        echo "  Starting Flask server... Press Ctrl+C to stop."
        python app.py
        ;;
    4)
        python main.py --batch
        ;;
    5)
        echo "  Running unit test discovery..."
        python -m unittest discover -s tests -v
        ;;
    6)
        echo "  Exiting Memora launcher."
        exit 0
        ;;
    *)
        echo "  Invalid selection. Defaulting to Interactive CLI..."
        python main.py
        ;;
esac
