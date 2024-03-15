@echo off

REM Check if virtual env 'myenv' exists
if not exist myenv (
    echo Creating virtual environment 'myenv'...
    python -m venv myenv
)

REM Activate the virtual environment
call myenv\Scripts\activate

REM Run main.py if customtkinter exists, otherwise run updater.py
python -c "import customtkinter" >nul 2>&1
if %errorlevel% equ 0 (
    echo Running main.py...
    python main.py
) else (
    echo Running updater.py...
    python updater.py
)

REM Deactivate the virtual environment
deactivate
