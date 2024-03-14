#!/bin/bash
source myenv/bin/activate
python -c "import sys; sys.exit(0 if __import__('importlib.util').find_spec('customtkinter') else 1)"
if [ $? -eq 0 ]; then
    python main.py
else
    python updater.py
fi
