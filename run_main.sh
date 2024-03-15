#!/bin/bash

# Activate the virtual environment
source myenv/bin/activate

# Attempt to import the module directly in Python
python -c "import sys, importlib; sys.exit(0 if importlib.util.find_spec('customtkinter') else 1)"

# Check the exit status of the previous command
if [ $? -eq 0 ]; then
    python main.py
else
    python updater.py
fi
