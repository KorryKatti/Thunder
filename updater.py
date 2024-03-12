import os
import shutil
import subprocess

def clone_repository(repo_url, destination_dir):
    subprocess.run(["git", "clone", repo_url, destination_dir])

def delete_files_except_current(file_dir):
    current_file = os.path.abspath(__file__)
    for file_name in os.listdir(file_dir):
        if file_name != os.path.basename(current_file):
            file_path = os.path.join(file_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

def copy_files(source_dir, destination_dir):
    for item in os.listdir(source_dir):
        source = os.path.join(source_dir, item)
        destination = os.path.join(destination_dir, item)
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

def main():
    # Clone the updated repository into a new folder
    repo_url = 'https://github.com/KorryKatti/Thunder.git'  # Replace with your GitHub repository URL
    newup_dir = 'newup'
    clone_repository(repo_url, newup_dir)

    # Delete all files except the current updater.py
    delete_files_except_current(os.path.dirname(__file__))

    # Copy files from newup to the current directory
    copy_files(newup_dir, os.path.dirname(__file__))

    # Delete the newup folder
    shutil.rmtree(newup_dir)

    # Display "Done" message
    print("Done")

if __name__ == "__main__":
    main()
