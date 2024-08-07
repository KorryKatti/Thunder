import customtkinter as ctk
import subprocess
import threading
from PIL import Image as PILImage
from PIL import ImageTk
import os
import stat
import time
import os
from tabulate import tabulate
import json
import platform
import shutil
import venv
from bs4 import BeautifulSoup
import re
import requests
from PIL import Image
import webview
import webbrowser
from io import BytesIO
import markdown
from tkinterhtml import HtmlFrame


# Launch repup.py in the background
subprocess.Popen(["python", "appfiles/repup.py"])

def print_thunder_pattern():
    thunder = """


@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@+.:@@@@@@@@@@@@@@..@@@@@@@@@@@@@@ .@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@..@@@@..@@@@@@@..@@@@@@@..@@@@..@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@ *@@@@@@..@@@..@@@@@....@@@@=.-@@@..@@.@@@:.@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@..@@@@@@@@.....@@@@@@@@+.-@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@%@@@@@@@@..@@@@@@.....#@@@@@@..@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@...@@@@@@@@@..@@@.......@@@@@@@@@@@@@@@. .@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@:.@@@@@@@@@........-@@@@@@@@@@.@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@=..@@@@@@..@@@@.........@@@@@@@.=@@@@@@...@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@........@@@@@@@@*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.......*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@...@@@@@@@@.................@@@@@@@....@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@.. .@@@@@@@@@@@@@@......@@@@@@@@+  .@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@..@@@@@@@@@@@@@@@@.......@@@@@@@@@@@@@..@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@.*@@@@@@@@@@@.......@@@@@@@@@@@ @@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@@..@@@.......@@@..@@@@@@-@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@.@@@@@@@@@@@@@@@@@@@.....@@@@@ .@@@@@@@@@@@=@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@..@@@@@@@....%@@@@@@+ %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@.@@@@@..@@@@@.@@@....@@@@..@@@+@@@@@@@.@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@.@@@@. .@@@@@@@@@@..:@@@@@..@@@@@@@@@@.@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@%..@@@@-@@@@@@..@@@@@@@- @@@..@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@..@@@@@@.@@@@@@..@@@@@@@@@@@@@@ .@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


"""
    print(thunder)

def print_welcome_message():
    print("Welcome To Thunder")



# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
#get theme from a dropdown
# Read the theme name from theme.txt
theme_file_path = "themes/theme.txt"
try:
    with open(theme_file_path, "r") as theme_file:
        theme_name = theme_file.read().strip()

    # Set the default color theme using the theme name
    ctk.set_default_color_theme(theme_name)
    print("Theme set successfully!")
    print_thunder_pattern()
    print_welcome_message()
    
except FileNotFoundError:
    print("Theme file not found.")

#useless function , for now
'''
def print_file_check_table(files_to_check):
    def check_file(file_path):
        return "✔️" if os.path.isfile(file_path) else "❌"

    table_data = []
    for file_name in files_to_check:
        file_status = check_file(file_name)
        table_data.append([file_name, file_status])

    headers = ["File", "Existence"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

files_to_check = ["main.py", "updater.py", "appfiles/repup.py"]
print_file_check_table(files_to_check)

'''

#what download does
def download_app():
    print("Download button clicked")

def quit(window):
    window.destroy()    

# Function to download image from URL and return PIL Image object
def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print(f"Error downloading image from URL: {url}. Error: {e}")
        return None
# Function to create labels for each application data
def create_labels():

    # messy code , i am aware
    search_bar = ctk.CTkEntry(scrollable_frame, placeholder_text="Search")
    search_bar.pack(side="top", fill="x", padx=20, pady=20)

    def search_labels(whatsearch):
        clear_scrollable_frame()

        data_dir = "data"
        filenames = sorted(os.listdir(data_dir), reverse=True)
        for filename in filenames:
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(data_dir, filename), "r") as f:
                        app_data = json.load(f)

                        app_frame = ctk.CTkFrame(scrollable_frame)
                        app_frame.pack(fill=ctk.X, padx=10, pady=5)
                        #for some reason its getting too big gaps when app is not in the order , if it makes sense
                        # TODO : remove blank spaces of apps not matching search criteria
                        app_name = app_data.get("app_name", "Unknown")
                        app_id = app_data.get("app_id", "Unknown")
                        description = app_data.get("description", "No description available")
                        if whatsearch.lower() in app_name.lower() or whatsearch.lower() in app_id.lower() or whatsearch.lower() in description.lower():
                            name_label = ctk.CTkLabel(app_frame, text="{app_name}, was found".format(app_name=app_name))
                            name_label.pack(side=ctk.TOP, padx=10, pady=5) #maybe changing pad will help with useless gap ?
                            # Display the application description
                            description = app_data.get("description", "No description available")
                            description_label = ctk.CTkLabel(app_frame, text=description, wraplength=700)
                            description_label.pack(side=ctk.TOP, padx=10, pady=5)

                            # Display the version
                            version = app_data.get("version", "Couldn't get version")
                            version_label = ctk.CTkLabel(app_frame, text=version, wraplength=700)
                            version_label.pack(side=ctk.LEFT, padx=10, pady=5)

                            # Create a button for downloading the application
                            download_button = ctk.CTkButton(app_frame, text="Download", command=lambda app=app_data: download_app(app))
                            download_button.pack(side=ctk.RIGHT, padx=10, pady=5)

                            # Create a separator line
                            separator = ctk.CTkLabel(scrollable_frame, text="--------------------------")
                            separator.pack(fill=ctk.X, padx=10, pady=5)
                        else:
                            print("Not found")

                except Exception as e:
                    print(f"Error loading data from {filename}: {e}")

    def clear_scrollable_frame():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

    def on_search(event=None):
        whatsearch = search_bar.get()
        print(whatsearch)
        search_labels(whatsearch)

    search_bar.bind("<Return>", on_search)
# search bar cloes now
    data_dir = "data"
    # Get the list of filenames and sort them
    filenames = sorted(os.listdir(data_dir) , reverse=True)
    for filename in filenames:
        if filename.endswith(".json"):
            try:
                with open(os.path.join(data_dir, filename), "r") as f:
                    app_data = json.load(f)

                    # Create a frame for each application data
                    app_frame = ctk.CTkFrame(scrollable_frame)
                    app_frame.pack(fill=ctk.X, padx=10, pady=5)

                    # Create a label for the application name
                    app_name = app_data.get("app_name", "Unknown")
                    name_label = ctk.CTkLabel(app_frame, text=app_name)
                    name_label.pack(side=ctk.TOP, padx=10, pady=5)

                    # Display the application description
                    description = app_data.get("description", "No description available")
                    description_label = ctk.CTkLabel(app_frame, text=description, wraplength=700)
                    description_label.pack(side=ctk.TOP, padx=10, pady=5)

                    # Display the version
                    version = app_data.get("version", "Couldn't get version")
                    version_label = ctk.CTkLabel(app_frame, text=version, wraplength=700)
                    version_label.pack(side=ctk.LEFT, padx=10, pady=5)

                    # Create a button for downloading the application
                    download_button = ctk.CTkButton(app_frame, text="Download", command=lambda app=app_data: download_app(app))
                    download_button.pack(side=ctk.RIGHT, padx=10, pady=5)

                    # Create a separator line
                    separator = ctk.CTkLabel(scrollable_frame, text="--------------------------")
                    separator.pack(fill=ctk.X, padx=10, pady=5)
            except Exception as e:
                print(f"Error processing JSON file {filename}: {e}")

# Function to display detailed information about the selected app
def download_app(app_data):
    # Clear the existing widgets in the scrollable frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Create a frame for displaying app details
    details_frame = ctk.CTkFrame(scrollable_frame)
    details_frame.pack(fill=ctk.X, padx=10, pady=5)

    # Display the application icon
    icon_url = app_data.get("icon_url", "")
    if icon_url:
        # Download the image from URL
        icon_image = download_image(icon_url)

        if icon_image:
            # Create a CTkImage object
            ct_image = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(100, 100))

            # Create a label to display the image
            image_label = ctk.CTkLabel(details_frame, image=ct_image, text="")
            image_label.pack(side=ctk.LEFT, padx=10, pady=5)

    # Create a label for the application name
    app_name = app_data.get("app_name", "Unknown")
    name_label = ctk.CTkLabel(details_frame, text=app_name, font=("Helvetica", 16, "bold"))
    name_label.pack(side=ctk.TOP, padx=10, pady=5)

    # Display the application description
    description = app_data.get("description", "No description available")
    description_label = ctk.CTkLabel(details_frame, text=description, wraplength=700)
    description_label.pack(side=ctk.TOP, padx=10, pady=5)

    # Display the version
    version = app_data.get("version", "Version not specified")
    version_label = ctk.CTkLabel(details_frame, text=f"Version: {version}")
    version_label.pack(side=ctk.TOP, padx=10, pady=5)

    # Create a button for downloading the repository
    download_repo_button = ctk.CTkButton(details_frame, text="Download Repository", command=lambda: download_repo(repo_url, app_data.get("app_id", ""), app_data.get("app_name", "")))
    download_repo_button.pack(side=ctk.TOP, padx=10, pady=5)

    # Fetch README content from the repository URL
    repo_url = app_data.get("repo_url", "")
    if repo_url:
        branches = ["main", "master"]  # Branches to check

        for branch in branches:
            try:
                response = requests.get(f"{repo_url}/raw/{branch}/Readme.md")
                response.raise_for_status()
                readme_content = response.text

                # Render Markdown content as HTML
                html_content = markdown.markdown(readme_content, output_format="html")

                # Create a TkinterHTML widget to display HTML content
                readme_html = HtmlFrame(details_frame)
                readme_html.set_content(html_content)
                readme_html.pack(side=ctk.TOP, padx=10, pady=5)



                break  # Break the loop if README content is successfully fetched
            except Exception as e:
                print(f"Error fetching README content for branch {branch}: {e}")
        else:
            print("Failed to fetch README content from any branch.")
    else:
        print("Repository URL not provided.")

# Create the main application window
app = ctk.CTk()
app.geometry("1152×648")
app.resizable(True, True)
app.title("Thunder 🗲")

#adding icon to app
icon_path = os.path.join("media", "icon.png")
icon_image = ImageTk.PhotoImage(file=icon_path)
app.iconphoto(False, icon_image)


def fetch_website_version(app_id):
    # URL of the website where version is located
    url = f"https://korrykatti.github.io/thapps/apps/{app_id}.html"

    # Fetch HTML content of the website
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content

        # Parse HTML content to extract version
        soup = BeautifulSoup(html_content, 'html.parser')
        version_tag = soup.find('h2', {'id': 'version'})
        if version_tag:
            return version_tag.text.strip()
        else:
            return None
    else:
        return None

def update_app(app_id, app_name, repo_url, app_dir):
    # Construct destination directory for cloning the repository
    destination_dir = os.path.join("common", f"{app_id}_{app_name}")

    # Clone the GitHub repository
    if clone_github_repo(repo_url, destination_dir):
        # Update successful, display message or perform any other action if needed
        print(f"App {app_id}_{app_name} updated successfully")
    else:
        # Update failed, display error message or perform any other action if needed
        print(f"Failed to update App {app_id}_{app_name}")


def clone_github_repo(repo_url, destination_dir):
    try:
        subprocess.run(["git", "clone", repo_url, destination_dir])
        print(f"Repository cloned successfully to {destination_dir}")
        return True
    except Exception as e:
        print(f"Error cloning repository: {e}")
        return False

# Define the callback function for the optionmenu
def optionmenu_callback(choice):
    print("Optionmenu dropdown clicked:", choice)
    if choice == "Quit":
        quit(app)
    elif choice == "Home":
        # Clear the existing widgets in the scrollable frame
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        # Create new labels for applications
        create_labels()
    elif choice == "Client Update":
        app.destroy()  # Close the current window
        subprocess.Popen(["python", "main.py"])  # Run main.py

# Function to get the repository URL from the app's JSON file
def get_repo_url(app_id):
    json_file = os.path.join("data", f"{app_id}.json")
    with open(json_file, "r") as f:
        data = json.load(f)
        return data.get("repo_url", "")

# Callback Function for Libmenu
def libmenu_callback(choice):
    if choice == "Library":
        # Clear the existing widgets in the scrollable frame
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Get the list of app IDs and names
        app_list = []
        data_dir = "data"
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(data_dir, filename), "r") as f:
                        app_data = json.load(f)
                        app_id = app_data.get("app_id", "")
                        app_name = app_data.get("app_name", "")

                        # Check if the app ID exists in downloads.txt
                        downloads_file = os.path.join("appfiles", "downloads.txt")
                        if os.path.exists(downloads_file):
                            with open(downloads_file, "r") as downloads:
                                if app_id.strip() in downloads.read().splitlines():
                                    app_list.append(f"{app_id}_{app_name}")
                except Exception as e:
                    print(f"Error processing JSON file {filename}: {e}")

        # Display the list of app IDs and names in the scrollable frame
        if app_list:
            for app_entry in app_list:
                app_button = ctk.CTkButton(scrollable_frame, text=app_entry, command=lambda app=app_entry: handle_app_click(app))
                app_button.pack(fill=ctk.NONE, padx=10, pady=(50, 5), anchor="w")
        else:
            # Display a message if no apps are available
            no_apps_label = ctk.CTkLabel(scrollable_frame, text="Download some apps first silly")
            no_apps_label.pack(fill=ctk.X, padx=10, pady=(10, 5), anchor="w")

            # Load the image
            notfound_path = "media/404.png" 
            notfound = PILImage.open(notfound_path)

            # Convert the image into a CTkImage object
            ctk_alpha = ctk.CTkImage(light_image=notfound, dark_image=notfound, size=(400,400))

            # Create a label to display the image
            notfound_label = ctk.CTkLabel(scrollable_frame, image=ctk_alpha, text= "")
            notfound_label.pack(fill=ctk.X, padx=10, pady=5)



    elif choice == "Apps Update":
        # Clear the existing widgets in the scrollable frame
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Get the list of app IDs and names
        app_list = []
        data_dir = "data"
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(data_dir, filename), "r") as f:
                        app_data = json.load(f)
                        app_id = app_data.get("app_id", "")
                        app_name = app_data.get("app_name", "")
                        app_list.append({"id": app_id, "name": app_name})
                except Exception as e:
                    print(f"Error processing JSON file {filename}: {e}")

        # Check for updates of installed apps
        for app_entry in app_list:
            app_id = app_entry['id']
            app_name = app_entry['name']
            app_dir = os.path.join("common", f"{app_id}_{app_name}")

            # Check if the app directory exists
            if os.path.exists(app_dir):
                # Check if config.json exists in the app directory
                config_file = os.path.join(app_dir, "config.json")
                if os.path.exists(config_file):
                    print(f"Config file found for app {app_id}: {config_file}")
                    # Fetch website version
                    website_version = fetch_website_version(app_id)
                    if website_version:
                        print(f"Website version for app {app_id}: {website_version}")
                        # Compare with local version and display appropriate message
                        with open(config_file, 'r') as cf:
                            config_data = json.load(cf)
                            app_version = config_data.get("version", "")
                            if app_version == website_version:
                                up_to_date_label = ctk.CTkLabel(scrollable_frame, text=f"App {app_id}_{app_name} is up to date.")
                                up_to_date_label.pack(fill=ctk.X, padx=10, pady=(10, 5), anchor="w")
                            else:
                                # Delete existing app directory
                                shutil.rmtree(app_dir)
                                # Display update button if versions don't match
                                repo_url = get_repo_url(app_id)  # Get repo URL
                                update_button = ctk.CTkButton(scrollable_frame, text=f"Click me to update App {app_id}_{app_name}", command=lambda app_id=app_id, app_name=app_name, repo_url=repo_url, app_dir=app_dir: update_app(app_id, app_name, repo_url, app_dir))
                                update_button.pack(fill=ctk.X, padx=10, pady=(10, 5), anchor="w")
                    else:
                        # Error fetching website version
                        print(f"Error fetching website version for app {app_id}")
                else:
                    # Display message if config file not found
                    no_config_label = ctk.CTkLabel(scrollable_frame, text=f"No config file found for app {app_id}, it was not designed to be updated.")
                    no_config_label.pack(fill=ctk.X, padx=10, pady=(10, 5), anchor="w")
            else:
                print(f"App directory not found: {app_dir}")

    # i am running out of names , this function displays the app data finally
def cherry(start_command, uninstall_command):
    
    # Create a new frame for displaying additional data
    cherry_frame = ctk.CTkFrame(scrollable_frame, width=400, height=400, bg_color="white")
    cherry_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, padx=10, pady=10)

    # Create a button to start the app
    start_button = ctk.CTkButton(cherry_frame, text="Start", command=start_command)
    start_button.pack(side=ctk.TOP, padx=10, pady=5)

    # Create a button to uninstall the app
    uninstall_button = ctk.CTkButton(cherry_frame, text="Uninstall", command=uninstall_command)
    uninstall_button.pack(side=ctk.TOP, padx=10, pady=5)



def remove_word_from_file(filename, word_to_remove):
    try:
        # Read the content of the file, remove the word, and write back
        with open(filename, 'r') as file:
            lines = [line.strip() for line in file if line.strip() != word_to_remove]

        with open(filename, 'w') as file:
            file.write('\n'.join(lines))
        
        print(f"Word '{word_to_remove}' removed from {filename} successfully.")
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    except Exception as e:
        print(f"Error removing word from {filename}: {e}")

def handle_app_click(app_id):
    try:
        # Extract only the numeric part from app_id
        numeric_app_id = re.sub(r'\D*(\d{5}).*', r'\1', app_id)

        # Load the app data from the JSON file in the data folder
        data_dir = "data"
        json_file_path = os.path.join(data_dir, f"{numeric_app_id}.json")
        if not os.path.exists(json_file_path):
            print(f"Error: JSON file for app {app_id} not found.")
            return

        with open(json_file_path) as json_file:
            app_data = json.load(json_file)

        # Construct the directory path for the app
        app_dir = os.path.join("common", app_id)
        
        # Check if the thunderenv directory exists in the app directory
        thunderenv_path = os.path.join(app_dir, "myenv")
        if os.path.exists(thunderenv_path) and os.path.isdir(thunderenv_path):
            print("Thunderenv found.")
        else:
            print("Thunderenv not found.")
            # Create a virtual environment named "thunderenv" in the app's folder
            try:
                venv.create(thunderenv_path, with_pip=True)
                print("Virtual environment created successfully.")
            except Exception as e:
                print(f"Error creating virtual environment: {e}")

        # Function to start the app
        # Function to start the app
        def start_app():
            try:
                # Check if the thunderenv directory exists in the app directory
                if os.path.exists(thunderenv_path) and os.path.isdir(thunderenv_path):
                    print("Thunderenv found. Starting the app...")

                    # Install requirements from requirements.txt if exists
                    requirements_file = os.path.join(app_dir, "requirements.txt")
                    if os.path.exists(requirements_file):
                        print("Installing requirements from requirements.txt...")
                        subprocess.run([os.path.join(thunderenv_path, "bin", "pip"), "install", "-r", requirements_file])
                        print("Requirements installed successfully.")

                    # Get the main file path from the app's JSON file
                    main_file_name = app_data.get("main_file", "")
                    main_file = os.path.join(app_dir, main_file_name)
                    maincdfile = main_file_name

                    if os.path.exists(main_file):
                        print("Launching the app...")
                        # Change the current working directory to app_dir
                        os.chdir(app_dir)
                        thundercdenv = "myenv"
                        if os.name == 'posix':  # For Linux
                            subprocess.run([os.path.join(thundercdenv, "bin", "python"), maincdfile])
                            os.chdir("../../")
                        elif os.name == 'nt':  # For Windows
                            subprocess.run([os.path.join(thundercdenv, "Scripts", "python.exe"), maincdfile])
                            os.chdir("../../")
                    else:
                        print("Main file not found.")
                        return  # Return if main file is not found
                else:
                    print("Thunderenv not found.")
            except Exception as e:
                print(f"Error starting the app in start app function : {e}")


        # Function to uninstall the app

        def uninstall_app():
            # Define the onerror handler function
            def onerror(func, path, exc_info):
                """
                Error handler for ``shutil.rmtree``.

                If the error is due to an access error (read only file)
                it attempts to add write permission and then retries.

                If the error is for another reason it re-raises the error.
                """
                # Is the error an access error?
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise

            # Delete the directory corresponding to the app
            try:
                # Attempt to remove the directory with the onerror handler
                shutil.rmtree(app_dir, onerror=onerror)
                print("App directory deleted successfully:", app_dir)
                
                # Remove app ID from downloads.txt
                downloads_file = os.path.join("appfiles", "downloads.txt")
                if os.path.exists(downloads_file):
                    print("downloads.txt exists.")
                    remove_word_from_file(downloads_file, numeric_app_id)
                else:
                    print("downloads.txt not found.")
            except FileNotFoundError:
                print(f"Error: {app_dir} not found.")
            except Exception as e:
                print(f"Error uninstalling the app: {e}")


        # Call cherry() with start and uninstall commands
        cherry(start_app, uninstall_app)

    except Exception as e:
        print(f"Error handling app click: {e}")



# CallBack function for commenu
def commenu_callback(choice):
    if choice == "Community":
        webbrowser.open("http://korrykatti.github.io/others/thunder/community.html")
    elif choice == "Image Board":
        webbrowser.open("http://korrykatti.github.io/others/thunder/image.html")
    elif choice == "Thunder Halls":
        webbrowser.open("http://korrykatti.github.io/others/thunder/halls.html")

import tkinterweb as tkweb
# huh , i should have removed these imports
import requests

# CallBack function for devmenu
import webview

# CallBack function for devmenu
def devmenu_callback(choice):
    # Clear existing widgets in the scrollable frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Display different content based on the choice
    if choice == "Dev Blog":
        # Create a TkinterHTML object
        html_frame = tkweb.HtmlFrame(scrollable_frame, width=864,height=486)
        html_frame.pack(padx=10, pady=10)  # Add padding for top margin

        # Load the website
        html_frame.load_url("https://korrykatti.github.io/thapps/data/index.html")



    elif choice == "Changelogs":
        # Fetch changelog from JSON file
        changelog_url = "https://korrykatti.github.io/thapps/data/changelog.json"
        try:
            response = requests.get(changelog_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            changelog_data = response.json()

            # Extract changelog data
            changelog_entries = changelog_data.get("changelog", [])

            # Display changelog
            for entry in changelog_entries:
                version = entry.get("version", "")
                changes = entry.get("changes", [])

                # Display version
                version_label = ctk.CTkLabel(scrollable_frame, text=f"**{version}**")
                version_label.pack(fill=ctk.X, padx=10, pady=5)

                # Display changes
                for change in changes:
                    change_label = ctk.CTkLabel(scrollable_frame, text=change)
                    change_label.pack(fill=ctk.X, padx=20, pady=2)

                # Add separator line
                separator = ctk.CTkLabel(scrollable_frame, text="------------------------------------------")
                separator.pack(fill=ctk.X, padx=10, pady=5)

        except Exception as e:
            print(f"Error fetching changelog: {e}")



#mozart from
# https://freemusicarchive.org/music/Brendan_Kinsella/Mozarts_Piano_Sonata_in_B-flat_Major/Mozart_-_Piano_Sonata_in_B-flat_major_III_Allegretto_Grazioso/
# Define the function to start playing the music after 11 seconds


def download_repo(repo_url, app_id, app_name):
    # Construct filename
    filename = f"{app_id}_{app_name}"

    # Check if the "common" directory exists, create if not
    common_dir = "common"
    if not os.path.exists(common_dir):
        os.makedirs(common_dir)

    # Create a directory for the specific app within the "common" directory
    app_dir = os.path.join(common_dir, filename)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    # Clone the GitHub repository specified by repo_url into the newly created directory
    subprocess.run(["git", "clone", repo_url, app_dir])

    # Check if downloads.txt exists in the "appfiles" folder and update it with the app_id if needed
    appfiles_dir = "appfiles"
    downloads_file = os.path.join(appfiles_dir, "downloads.txt")
    if os.path.exists(downloads_file):
        with open(downloads_file, "a") as f:
            f.write(app_id + "\n")

    else:
        with open(downloads_file, "w") as f:
            f.write(f"{app_id}\n")

    # Create a top-up window for downloading repository
    download_window = ctk.CTkToplevel(app)
    download_window.geometry("400x300")
    download_window.title("Download Repository")

    label = ctk.CTkLabel(download_window, text="Downloading Repository")
    label.pack(padx=20, pady=20)

    # Create a progress bar for showing download progress
    progress_bar = ctk.CTkProgressBar(download_window, orientation="horizontal", mode="indeterminate")
    progress_bar.pack(padx=20, pady=10)
    progress_bar.start()  # Start the progress bar animation   

    # Function to close the top-up window
    def close_window():
        download_window.destroy()

    # Close the top-up window after 3 seconds
    download_window.after(3000, close_window)

# most of the themes are from https://github.com/a13xe/CTkThemesPack and https://github.com/rigvedmaanas/CustomTkinterThemes
def theme_set(choice):
    with open("themes/theme.txt", "w") as f:
        if choice == "Default":
            f.write("")
        elif choice == "Orange":
            f.write("themes/orange.json")
        elif choice == "Green":
            f.write("themes/green.json")
        elif choice =="Coffee":
            f.write("themes/coffee.json")
        elif choice =="Violet":
            f.write("themes/violet.json")
        elif choice =="Blue":
            f.write("themes/blue.json")
        elif choice =="Carrot":
            f.write("themes/carrot.json")
        elif choice =="Cyberpunk":
            f.write("themes/cyberpunk.json")
        elif choice =="Marsh":
            f.write("themes/marsh.json")
        elif choice =="Metal":
            f.write("themes/metal.json")
        elif choice == "Pink":
            f.write("themes/pink.json")
        elif choice == "Red":
            f.write("themes/red.json")
        elif choice == "Rose":
            f.write("themes/rose.json")
        elif choice == "Sky":
            f.write("themes/sky.json")
        elif choice == "Yellow":
            f.write("themes/yellow.json")
        elif choice == "FlipperZero":
            f.write("themes/flipperzero.json")
        elif choice == "hacked":
            f.write("themes/hacked.json")
    f.close()
    app.destroy()  # Close the current window
    subprocess.Popen(["python", "index.py"])


# Create a frame inside the main window for organizing widgets
# Create the main frame
mainframe = ctk.CTkFrame(app)
mainframe.pack(expand=True, fill="both")  # Pack the main frame to fill the window

# Create the frame for organizing widgets
frame = ctk.CTkFrame(mainframe, width=200)
frame.pack(fill="x")

# Create the optionmenu widget
optionmenu = ctk.CTkOptionMenu(frame, values=["Home", "Client Update", "Quit"],
                                command=optionmenu_callback)
optionmenu.pack(pady=(10, 10), expand=True, side="left")

# Create the library menu widget
libmenu = ctk.CTkOptionMenu(frame, values=["Library", "Apps Update"],
                            command=libmenu_callback)
libmenu.pack(pady=(10, 10), expand=True, side="left")

# Create the Community Widget
commenu = ctk.CTkOptionMenu(frame, values=["Community", "Image Board", "Thunder Halls"],
                             command=commenu_callback)
commenu.pack(pady=(10, 10), expand=True, side="left")

# Create DevBlogs Widget
devmenu = ctk.CTkOptionMenu(frame, values=["Dev Blog", "Changelogs"],
                             command=devmenu_callback)
devmenu.pack(pady=(10, 10), expand=True, side="left")

# Create the theme selector
thememenu = ctk.CTkOptionMenu(frame, values=["Default","Orange","Green","Coffee","Violet","Blue","Cyberpunk","Carrot","Marsh","Metal","Pink","Red","Rose","Sky","Yellow","FlipperZero","hacked"],
                               command=theme_set)
thememenu.pack(pady=(10, 10), expand=True, side="left")

# Load the image
alpha_path = "media/grass.png" 
alpha = PILImage.open(alpha_path)

# Convert the image into a CTkImage object
ctk_alpha = ctk.CTkImage(light_image=alpha, dark_image=alpha, size=(1280, 100))

# Create a label to display the image
alpha_label = ctk.CTkLabel(mainframe, image=ctk_alpha, text ="")
alpha_label.pack(padx=20, pady=20, fill="x")  # Adjust padding and alignment as needed

# Create a scrollable frame inside the existing main frame to display contents
scrollable_frame = ctk.CTkScrollableFrame(mainframe, width=1024, height=576, corner_radius=0, fg_color="transparent")
scrollable_frame.pack(expand=True, fill="both")



# Add widgets to the scrollable frame
create_labels()

# Start the main event loop
app.mainloop()
