#!/bin/bash

# Simple Virtual Environment Activation Script
# Usage: source activate_simple.sh   (NOT ./activate_simple.sh)

# Check if script is being sourced (not executed)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "❌ ERROR: This script must be sourced, not executed!"
    echo "✅ Correct usage: source activate_simple.sh"
    echo "✅ Or use: . activate_simple.sh"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define venv path relative to script directory
VENV_PATH="$SCRIPT_DIR/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Virtual environment not found at: $VENV_PATH"
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        return 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment from: $VENV_PATH"
source "$VENV_PATH/bin/activate"

# Verify activation
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Virtual environment activated successfully!"
    echo "Python: $(which python)"
    echo "Location: $VIRTUAL_ENV"
    echo "To deactivate: deactivate"
else
    echo "❌ Failed to activate virtual environment"
    return 1
fi
