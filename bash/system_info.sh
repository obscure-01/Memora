#!/bin/bash
# ==============================================================================
# Memora — system_info.sh
# Displays relevant system information for documentation and debugging.
#
# Usage (from Git Bash on Windows):
#   bash bash/system_info.sh
#
# Designed for Git Bash on Windows. Uses Windows-compatible commands
# with fallbacks where necessary.
#
# Phase 1: Functional. Reports basic environment info.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================"
echo "  Memora — System Information"
echo "============================================"
echo ""

# Operating System
echo "  Operating System:"
if command -v systeminfo &>/dev/null; then
    SYS_INFO=$(systeminfo 2>/dev/null)
    OS_NAME=$(echo "$SYS_INFO" | grep "OS Name" | head -1 | sed 's/.*: *//')
    OS_VER=$(echo "$SYS_INFO" | grep "OS Version" | head -1 | sed 's/.*: *//')
    echo "    Name:    ${OS_NAME:-Unknown}"
    echo "    Version: ${OS_VER:-Unknown}"
else
    echo "    $(uname -s 2>/dev/null || echo 'Unknown') $(uname -r 2>/dev/null || echo '')"
fi
echo ""

# Shell
echo "  Shell:"
echo "    SHELL:   ${SHELL:-Unknown}"
echo "    Bash:    ${BASH_VERSION:-Unknown}"
echo ""

# Python
echo "  Python:"
if command -v python &>/dev/null; then
    echo "    Version: $(python --version 2>&1)"
    echo "    Path:    $(command -v python)"
else
    echo "    [NOT FOUND] Python is not on PATH."
fi
echo ""

# Pip
echo "  Pip:"
if command -v pip &>/dev/null; then
    echo "    Version: $(pip --version 2>&1)"
else
    echo "    [NOT FOUND] pip is not on PATH."
fi
echo ""

# Git
echo "  Git:"
if command -v git &>/dev/null; then
    echo "    Version: $(git --version 2>&1)"
else
    echo "    [NOT FOUND] Git is not on PATH."
fi
echo ""

# Virtual Environment
echo "  Virtual Environment:"
VENV_ACTIVATE="$PROJECT_ROOT/venv/Scripts/activate"
ALT_VENV_ACTIVATE="$PROJECT_ROOT/.venv/Scripts/activate"
if [ -f "$VENV_ACTIVATE" ]; then
    echo "    Status: Found at venv/"
elif [ -f "$ALT_VENV_ACTIVATE" ]; then
    echo "    Status: Found at .venv/"
else
    echo "    Status: Not created yet"
fi
echo ""

# Project
echo "  Project:"
echo "    Root: $PROJECT_ROOT"
echo "    Main: $PROJECT_ROOT/main.py"
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "    Dependencies:"
    while IFS= read -r line; do
        [[ -z "$line" || "$line" == \#* ]] && continue
        echo "      - $line"
    done < "$PROJECT_ROOT/requirements.txt"
fi
echo ""
echo "============================================"
