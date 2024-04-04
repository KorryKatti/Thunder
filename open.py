import os
import subprocess
import sys

# Function to check if a directory exists
def directory_exists(directory):
    return os.path.exists(directory)

# Function to create a virtual environment
def create_venv(directory):
    os.system(f"{sys.executable} -m venv {directory}")

# Function to install customtkinter (assuming it's a package)
def install_customtkinter(venv_directory):
    os.system(f"{os.path.join(venv_directory, 'bin', 'python')} -m pip install customtkinter")

# Function to run main.py using the Python interpreter from the virtual environment
def run_main_py(venv_directory):
    python_executable = os.path.join(venv_directory, "bin", "python")
    main_script = "main.py"
    subprocess.run([python_executable, main_script])

# Function to run updater.py using the Python interpreter from the virtual environment
def run_updater_py(venv_directory):
    python_executable = os.path.join(venv_directory, "bin", "python")
    updater_script = "updater.py"
    subprocess.run([python_executable, updater_script])

def main():
    venv_directory = "myenv"

    if not directory_exists(venv_directory):
        create_venv(venv_directory)

    try:
        # Check if customtkinter is importable
        import customtkinter
    except ImportError:
        # If not importable, run updater.py
        run_updater_py(venv_directory)
        return

    install_customtkinter(venv_directory)
    run_main_py(venv_directory)

if __name__ == "__main__":
    main()
