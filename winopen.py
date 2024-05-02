import os
import subprocess
import sys
import shutil
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

def main():
    # Delete the "update" folder if it exists
    update_folder = "update"
    if os.path.exists(update_folder):
        # Use shutil.rmtree with onerror handler
        shutil.rmtree(update_folder, onerror=onerror)

    venv_directory = "myenv"

    if not os.path.exists(venv_directory):
        subprocess.run([sys.executable, "-m", "venv", venv_directory], shell=True)

    activate_script = os.path.join(venv_directory, "bin", "activate")
    subprocess.run(["source", activate_script], shell=True)

    python_executable = os.path.join(venv_directory, "bin", "python")
    subprocess.run([python_executable, "updater.py"], shell=True)

if __name__ == "__main__":
    main()
