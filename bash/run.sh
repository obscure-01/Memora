#!/bin/bash
# ==============================================================================
# Memora — run.sh
# Main launcher script for the Memora virtual memory simulator.
#
# Usage (from Git Bash on Windows):
#   bash bash/run.sh
#
# This script:
#   1. Detects the project root directory.
#   2. Activates the Python virtual environment (if it exists).
#   3. Launches main.py.
#
# Phase 1: Scaffolding. Full argument-passing support planned for Phase 2.
# ==============================================================================

set -e

# --- Detect project root (directory containing this script's parent) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================"
echo "  Memora — Virtual Memory Simulator"
echo "============================================"
echo "  Project root: $PROJECT_ROOT"
echo ""

# --- Activate virtual environment ---
VENV_ACTIVATE="$PROJECT_ROOT/venv/Scripts/activate"
ALT_VENV_ACTIVATE="$PROJECT_ROOT/.venv/Scripts/activate"

if [ -f "$VENV_ACTIVATE" ]; then
    echo "  Activating virtual environment (venv)..."
    source "$VENV_ACTIVATE"
    echo "  Python: $(python --version 2>&1)"
elif [ -f "$ALT_VENV_ACTIVATE" ]; then
    echo "  Activating virtual environment (.venv)..."
    source "$ALT_VENV_ACTIVATE"
    echo "  Python: $(python --version 2>&1)"
else
    echo "  [WARNING] Virtual environment not found at: venv/ or .venv/"
    echo "  Using system Python: $(python --version 2>&1)"
    echo "  To create a virtual environment, run:"
    echo "    python -m venv venv"
    echo "    venv\\Scripts\\activate   (CMD)"
    echo "    source venv/Scripts/activate   (Git Bash)"
    echo "    pip install -r requirements.txt"
    echo ""
fi

# --- Launch Memora ---
echo "  Launching Memora..."
echo "============================================"
echo ""

cd "$PROJECT_ROOT"
python main.py "$@"
