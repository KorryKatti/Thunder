import os
import shutil
import subprocess
import sys
import stat  # Import stat module for file permissions

# Define the onerror handler function
def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        # Attempt to add write permission
        os.chmod(path, stat.S_IWUSR)
        # Retry the operation
        func(path)
    else:
        # If the error is for another reason, re-raise the error
        raise

# Function to check if a directory exists
def directory_exists(directory):
    return os.path.exists(directory)

# Function to create a virtual environment
def create_venv(directory):
    os.system(f"{sys.executable} -m venv {directory}")

# Function to install required modules
def install_required_modules(venv_directory):
    required_modules = [
        "requests",
        "customtkinter",
        "beautifulsoup4"
    ]
    for module in required_modules:
        os.system(f"{os.path.join(venv_directory, 'bin', 'python')} -m pip install {module}")

# Function to activate the virtual environment on Windows
def activate_venv_windows(directory):
    return f"call {directory}\\Scripts\\activate"

# Function to activate the virtual environment on Linux
def activate_venv_linux(directory):
    return f"source {directory}/bin/activate"

# Function to run main.py or updater.py using the Python interpreter from the virtual environment
def run_script_py(venv_directory, script_name):
    python_executable = os.path.join(venv_directory, "Scripts", "python" if os.name == 'nt' else "bin", "python")
    script_path = f"{script_name}.py"
    subprocess.run([python_executable, script_path])

def main():
    venv_directory = "myenv"

    # Delete the "update" folder if it exists
    update_folder = "update"
    if directory_exists(update_folder):
        # Use shutil.rmtree with onerror handler
        shutil.rmtree(update_folder, onerror=onerror)

    if not directory_exists(venv_directory):
        create_venv(venv_directory)

    # Install required modules
    install_required_modules(venv_directory)

    try:
        # Check if customtkinter is importable
        import customtkinter
    except ImportError:
        activate_command = activate_venv_windows(venv_directory) if os.name == 'nt' else activate_venv_linux(venv_directory)
        try:
            subprocess.run(f"{activate_command} && python updater.py", shell=True)
        except Exception as e:
            print(f"Error activating virtual environment and running updater.py: {e}")
        return

    run_script_py(venv_directory, "main")

if __name__ == "__main__":
    main()
