@echo off

if not exist myenv (
    python -m venv myenv
)

call myenv\Scripts\activate.bat
myenv\Scripts\python.exe -c "import sys; sys.exit(0 if __import__('importlib.util').find_spec('customtkinter') else 1)"
if %errorlevel% equ 0 (
    myenv\Scripts\python.exe main.py
) else (
    myenv\Scripts\python.exe updater.py
)
