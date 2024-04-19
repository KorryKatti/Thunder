import os
import subprocess
import sys

# Function to create a virtual environment
def create_venv(directory):
    subprocess.run([sys.executable, "-m", "venv", directory], shell=True)

# Function to activate the virtual environment on Windows
def activate_venv(directory):
    activate_script = os.path.join(directory, "Scripts", "activate")
    subprocess.run([activate_script], shell=True)

# Function to run updater.py using the Python interpreter from the virtual environment
def run_updater(venv_directory):
    python_executable = os.path.join(venv_directory, "Scripts", "python")
    updater_script = "updater.py"
    subprocess.run([python_executable, updater_script], shell=True)

def main():
    venv_directory = "myenv"

    if not os.path.exists(venv_directory):
        create_venv(venv_directory)

    activate_venv(venv_directory)
    run_updater(venv_directory)

if __name__ == "__main__":
    main()
