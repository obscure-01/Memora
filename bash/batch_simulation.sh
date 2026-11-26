#!/bin/bash
# ==============================================================================
# Memora — batch_simulation.sh
# Automates running simulations across all sample datasets.
#
# Usage (from Git Bash on Windows):
#   bash bash/batch_simulation.sh
#
# This script executes simulations across all predefined datasets in
# datasets/sample_input.json and exports aggregated reports to results/reports/.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================"
echo "  Memora — Batch Simulation"
echo "============================================"
echo ""

# Activate venv if available
VENV_ACTIVATE="$PROJECT_ROOT/venv/Scripts/activate"
ALT_VENV_ACTIVATE="$PROJECT_ROOT/.venv/Scripts/activate"
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
elif [ -f "$ALT_VENV_ACTIVATE" ]; then
    source "$ALT_VENV_ACTIVATE"
fi

# Check for datasets
DATASET_FILE="$PROJECT_ROOT/datasets/sample_input.json"
if [ ! -f "$DATASET_FILE" ]; then
    echo "  [ERROR] Dataset file not found: $DATASET_FILE"
    exit 1
fi

cd "$PROJECT_ROOT"
python main.py --batch "$@"
