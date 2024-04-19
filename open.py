import subprocess
import os
import shutil
import sys
import stat  # Import stat module for file permissions

# Define the onerror handler function
def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise

# Function to check if a directory exists
def directory_exists(directory):
    return os.path.exists(directory)

# Function to create a virtual environment
def create_venv(directory):
    subprocess.run([sys.executable, "-m", "venv", directory])

# Function to install required modules
def install_required_modules(venv_directory):
    required_modules = [
        "requests",
        "customtkinter",
        "beautifulsoup4"
    ]
    subprocess.run([os.path.join(venv_directory, 'bin' if os.name != 'nt' else 'Scripts', 'pip'), "install", *required_modules])

# Function to activate the virtual environment
def activate_venv(directory):
    activate_script = os.path.join(directory, "Scripts" if os.name == 'nt' else "bin", "activate")
    # Ensure the script has executable permissions
    os.chmod(activate_script, stat.S_IRWXU)
    subprocess.run([activate_script], shell=True)

# Function to run main.py or updater.py using the Python interpreter from the virtual environment
def run_script_py(venv_directory, script_name):
    python_executable = os.path.join(venv_directory, "Scripts" if os.name == 'nt' else "bin", "python")
    script_path = f"{script_name}.py"
    subprocess.run([python_executable, script_path])

def main():
    venv_directory = "myenv"

    # Delete the "update" folder if it exists
    update_folder = "update"
    if directory_exists(update_folder):
        try:
            shutil.rmtree(update_folder, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Error deleting 'update' folder: {e}")

    if not directory_exists(venv_directory):
        create_venv(venv_directory)
        # Install required modules after creating the virtual environment
        install_required_modules(venv_directory)

    try:
        # Check if customtkinter is importable
        import customtkinter
    except ImportError:
        activate_venv(venv_directory)
        run_script_py(venv_directory, "updater")
        return

    activate_venv(venv_directory)
    run_script_py(venv_directory, "main")

if __name__ == "__main__":
    main()
