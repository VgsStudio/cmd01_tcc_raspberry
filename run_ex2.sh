#!/bin/bash
# OLED Beating Heart Script - Ex2
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python script using the virtual environment
sudo "$SCRIPT_DIR/venv/bin/python" ex2.py
