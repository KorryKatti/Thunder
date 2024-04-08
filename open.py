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

# Function to install customtkinter (assuming it's a package)
def install_customtkinter(venv_directory):
    os.system(f"{os.path.join(venv_directory, 'bin', 'python' if os.name != 'nt' else 'Scripts', 'pip')} install customtkinter")

# Function to activate the virtual environment
def activate_venv(directory):
    if os.name == 'nt':
        activate_script = os.path.join(directory, "Scripts", "activate")
        return f"call {activate_script}"
    else:
        activate_script = os.path.join(directory, "bin", "activate")
        return f"source {activate_script}"

# Function to run main.py or updater.py using the Python interpreter from the virtual environment
def run_script_py(venv_directory, script_name):
    if os.name == 'nt':
        activate_command = activate_venv(venv_directory)
        script_path = f"{script_name}.py"
        subprocess.run(f"{activate_command} && python {script_path}", shell=True)
    else:
        python_executable = os.path.join(venv_directory, "bin", "python")
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

    try:
        # Check if customtkinter is importable
        import customtkinter
    except ImportError:
        print("Customtkinter not found, attempting to run updater.py...")
        activate_command = activate_venv(venv_directory)
        print(f"Activate Command: {activate_command}")
        try:
            subprocess.run(f"{activate_command} && python updater.py", shell=True)
        except Exception as e:
            print(f"Error activating virtual environment and running updater.py: {e}")
        return

    print("Customtkinter found, installing...")
    install_customtkinter(venv_directory)
    run_script_py(venv_directory, "main")


if __name__ == "__main__":
    main()
