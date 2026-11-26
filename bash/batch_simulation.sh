#!/bin/bash
# ==============================================================================
# Memora — batch_simulation.sh
# Automates running simulations across predefined datasets.
#
# Usage (from Git Bash on Windows or Linux):
#   bash bash/batch_simulation.sh
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "========================================================================"
echo "  Memora — Automated Batch Simulation Runner"
echo "========================================================================"
echo ""

# Activate venv if available
VENV_ACTIVATE="$PROJECT_ROOT/venv/Scripts/activate"
ALT_VENV_ACTIVATE="$PROJECT_ROOT/.venv/Scripts/activate"
LINUX_VENV="$PROJECT_ROOT/venv/bin/activate"

if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
elif [ -f "$ALT_VENV_ACTIVATE" ]; then
    source "$ALT_VENV_ACTIVATE"
elif [ -f "$LINUX_VENV" ]; then
    source "$LINUX_VENV"
fi

DATASET_FILE="$PROJECT_ROOT/datasets/sample_input.json"
if [ ! -f "$DATASET_FILE" ]; then
    echo "  [ERROR] Dataset file not found: $DATASET_FILE"
    exit 1
fi

cd "$PROJECT_ROOT"
python main.py --batch "$@"
