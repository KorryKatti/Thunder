import json
import requests
import customtkinter as ctk
from bs4 import BeautifulSoup
import subprocess
import os
import stat
import shutil

def read_version():
    with open('config.json', 'r') as f:
        config_data = json.load(f)
        version = config_data.get('version', '0.0.0')
    return version


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

def get_external_version(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Modify the below line according to the structure of the external website's HTML
        version_element = soup.find('h1', {'id': 'version'})
        if version_element:
            return version_element.text.strip()
    return None

def close_window(window):
    window.destroy()

def compare_versions():
    # Call the function to delete the update folder
    delete_update_folder()

    local_version = read_version()
    external_url = 'https://korrykatti.github.io/others/thunder/version.html'  # Replace this with the actual URL of the external website
    external_version = get_external_version(external_url)
    if external_version:
        if local_version == external_version:
            result_message = f"You are up to date: {local_version}"
        else:
            result_message = f"Software is not up to date. Initializing Update.\nLocal version: {local_version}\nExternal version: {external_version}"
    else:
        result_message = "Failed to retrieve external version. Continuing either way to app"

    # Create a customtkinter window to display the results
    app = ctk.CTk()
    app.geometry("400x200")
    app.title("Version Comparison")

    label = ctk.CTkLabel(app, text=result_message, wraplength=380)
    label.pack(pady=20)

    # Close the window after 3 seconds
    app.after(3000, close_window, app)

    app.mainloop()

    # Perform actions based on version comparison result
    if local_version == external_version:
        # Same version, continue to index.py
        subprocess.run(["python", "index.py"])
    else:
        # Different version, open updater.py
        subprocess.run(["python", "updater.py"])

if __name__ == '__main__':
    compare_versions()
