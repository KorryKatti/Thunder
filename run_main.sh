#!/bin/bash

# Check if virtual env 'myenv' exists
if [ ! -d "myenv" ]; then
    echo "Creating virtual environment 'myenv'..."
    python3 -m venv myenv
fi

# Activate the virtual environment
source myenv/bin/activate

# Run main.py if customtkinter exists, otherwise run updater.py
if python -c "import customtkinter" &> /dev/null; then
    echo "Running main.py..."
    python main.py
else
    echo "Running updater.py..."
    python updater.py
fi

# Deactivate the virtual environment
deactivate
