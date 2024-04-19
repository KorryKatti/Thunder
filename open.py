import subprocess
import os
import shutil

def create_activate_venv(venv_name):
    # Check if venv directory exists
    venv_path = os.path.join(os.getcwd(), venv_name)
    if not os.path.exists(venv_path):
        # If venv directory doesn't exist, create it
        subprocess.run(["python", "-m", "venv", venv_name])
    
    # Activate virtual environment
    activate_script = os.path.join(venv_path, "Scripts", "activate")
    subprocess.run(["source" if os.name != "nt" else "cmd", activate_script])

def install_required_modules():
    # List of required modules
    required_modules = [
        "requests",
        "customtkinter",
        "beautifulsoup4"
    ]
    
    # Install required modules
    subprocess.run(["pip", "install", *required_modules])

def check_install_run():
    # Check if required modules are installed
    try:
        import requests
        import customtkinter as ctk
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"Error: {e.name} module not found.")
        print("Installing required modules...")
        install_required_modules()
    
    # Run main.py
    subprocess.run(["python", "main.py"])

def delete_update_folder():
    # Delete "update" folder if it exists
    update_folder = os.path.join(os.getcwd(), "update")
    if os.path.exists(update_folder):
        try:
            shutil.rmtree(update_folder, onerror=handle_remove_readonly)
            print("Deleted 'update' folder.")
        except Exception as e:
            print(f"Error deleting 'update' folder: {e}")

def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise

def main():
    venv_name = "myenv"
    delete_update_folder()
    create_activate_venv(venv_name)
    check_install_run()

if __name__ == "__main__":
    main()
