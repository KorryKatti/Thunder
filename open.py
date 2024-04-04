import os
import shutil
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

# Function to activate the virtual environment
def activate_venv(directory):
    activate_script = os.path.join(directory, "bin", "activate")
    return f"source {activate_script}"

# Function to run main.py or updater.py using the Python interpreter from the virtual environment
def run_script_py(venv_directory, script_name):
    python_executable = os.path.join(venv_directory, "bin", "python")
    script_path = f"{script_name}.py"
    subprocess.run([python_executable, script_path])

def main():
    venv_directory = "myenv"

    # Delete the "update" folder if it exists
    update_folder = "update"
    if directory_exists(update_folder):
        shutil.rmtree(update_folder)

    if not directory_exists(venv_directory):
        create_venv(venv_directory)

    try:
        # Check if customtkinter is importable
        import customtkinter
    except ImportError:
        # If not importable, run updater.py
        activate_command = activate_venv(venv_directory)
        subprocess.run(f"{activate_command} && python updater.py", shell=True)
        return

    install_customtkinter(venv_directory)
    run_script_py(venv_directory, "main")

if __name__ == "__main__":
    main()
