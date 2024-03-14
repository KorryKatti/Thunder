import os
import shutil
import subprocess
import sys

def clone_repository(repo_url, destination_dir):
    os.makedirs(destination_dir, exist_ok=True)  # Ensure the directory exists
    subprocess.run(["git", "clone", repo_url, destination_dir])

def copy_files(source_dir, destination_dir):
    for item in os.listdir(source_dir):
        source = os.path.join(source_dir, item)
        destination = os.path.join(destination_dir, item)
        if os.path.isdir(source):
            if not os.path.exists(destination):
                shutil.copytree(source, destination)
            else:
                copy_files(source, destination)  # Recursively copy subdirectories
        else:
            # Exclude .git directory
            if ".git" in source:
                continue
            shutil.copy2(source, destination, follow_symlinks=False)

def main():
    # Clone the updated repository into a new folder
    repo_url = 'https://github.com/KorryKatti/Thunder.git'  # Replace with your GitHub repository URL
    update_dir = 'update'
    clone_repository(repo_url, update_dir)

    # Copy files from update to the current directory
    copy_files(update_dir, os.path.dirname(__file__))

    # Get path to appfiles directory
    appfiles_dir = os.path.join(os.path.dirname(__file__), "appfiles")

    # Execute shell script to activate environment and install requirements
    if sys.platform == 'win32':  # Windows
        script_path = os.path.join(appfiles_dir, "activate_env.bat")
        subprocess.run([script_path], shell=True)
    else:  # Unix-like OS (Linux/Mac)
        script_path = os.path.join(appfiles_dir, "activate_env.sh")
        subprocess.run(["bash", "-c", f"source {script_path}"], shell=True)

if __name__ == "__main__":
    main()
