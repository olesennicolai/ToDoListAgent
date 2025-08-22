#!/bin/bash
# Script to ensure all Python commands use the virtual environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found at $VENV_PYTHON"
    echo "Run ./setup.sh to create it"
    exit 1
fi

# Run the command with venv python
"$VENV_PYTHON" "$@"