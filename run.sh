#!/bin/bash
set -e  # Exit immediately if a command fails

# Define environment name
VENV_DIR=".venv"

# Create venv if not exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate the environment
source "$VENV_DIR/bin/activate"

# Upgrade pip (optional but recommended)
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "✅ Environment setup complete."


SCRIPT="run.py"

# Run the Python script
echo "Running $SCRIPT..."
python "$SCRIPT"
