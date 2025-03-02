#!/bin/bash

# Script to run the Veue application with the virtual environment activated

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please set up the environment first."
    echo "Run: python -m venv venv"
    exit 1
fi

# Activate virtual environment and run the application
source venv/bin/activate
python main.py

# Deactivate the virtual environment when the application exits
deactivate

echo "Application closed." 