@echo off
call myenv\Scripts\activate.bat
python -c "import sys; sys.exit(0 if __import__('importlib.util').find_spec('customtkinter') else 1)"
if %errorlevel% equ 0 (
    python main.py
) else (
    python updater.py
)
