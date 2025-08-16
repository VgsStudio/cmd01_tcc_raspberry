#!/bin/bash
# LED Test Runner Script - Exp1
# Get the project root directory (parent of scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to the project directory
cd "$PROJECT_DIR"

# Run the Python script using the virtual environment
sudo "$PROJECT_DIR/venv/bin/python" experiments/exp1.py
