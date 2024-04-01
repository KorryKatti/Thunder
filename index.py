import customtkinter as ctk
import subprocess
import os
import json
import shutil
import venv
import re
import requests
from PIL import Image
import webview
from io import BytesIO
import markdown
from tkinterhtml import HtmlFrame

# Launch repup.py in the background
subprocess.Popen(["python", "appfiles/repup.py"])

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

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
# Function to create labels for each application data
def create_labels():
    data_dir = "data"
    for filename in os.listdir(data_dir):
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
app.geometry("1280x720")
app.resizable(True, True)
app.title("Thunder 🗲")

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
        subprocess.Popen(["python", "updater.py"])  # Run updater.py

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
    elif choice == "Apps Update":
        # Code to handle the "Apps Update" option
        pass

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


import os
import re
import shutil

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

        # Construct the directory path for the app
        app_dir = os.path.join("common", app_id)
        
        # Check if the thunderenv directory exists in the app directory
        thunderenv_path = os.path.join(app_dir, "thunderenv")
        if os.path.exists(thunderenv_path) and os.path.isdir(thunderenv_path):
            print("Yes")
        else:
            print("No")
            # Create a virtual environment named "thunderenv" in the app's folder
            try:
                venv.create(thunderenv_path, with_pip=True)
                print("Virtual environment created successfully.")
            except Exception as e:
                print(f"Error creating virtual environment: {e}")

        # Function to start the app
        def start_app():
            # Add your logic here to start the app
            print("Starting the app...")

        # Function to uninstall the app
        def uninstall_app():
            # Delete the directory corresponding to the app
            try:
                shutil.rmtree(app_dir)
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
        # Create a GUI window to view the HTML content
        webview.create_window('example', 'http://example.com')
        webview.start()
    elif choice == "Image Board":
        pass  # Placeholder for Image Board option logic
    elif choice == "Thunder Halls":
        pass  # Placeholder for Thunder Halls option logic

# CallBack function for devmenu
def devmenu_callback():
    pass

#functions for optionmenu
def quit(window):
    window.destroy()    

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
            f.write(f"{app_id}\n")
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

    # Function to close the top-up window after 3 seconds
    def close_window():
        download_window.destroy()

    # Schedule the close_window function to be called after 3 seconds
    download_window.after(3000, close_window)    

# Create a frame inside the main window for organizing widgets
frame = ctk.CTkFrame(app)
frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Pack the frame to fill the window

# Create the optionmenu widget
optionmenu = ctk.CTkOptionMenu(frame, values=["Home", "Client Update", "Quit"],
                                         command=optionmenu_callback)
optionmenu.grid(row=0, column=0, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create the library menu widget
libmenu = ctk.CTkOptionMenu(frame, values=["Library", "Apps Update"],
                                         command=libmenu_callback)
libmenu.grid(row=0, column=1, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create the Commmunity Widget
commenu = ctk.CTkOptionMenu(frame, values=["Community", "Image Board", "Thunder Halls"],
                                         command=commenu_callback)
commenu.grid(row=0, column=2, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create DevBlogs Widget
devmenu = ctk.CTkOptionMenu(frame,values=["Dev Blog", "Changelogs"],
                                         command=devmenu_callback)
devmenu.grid(row=0, column=3, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create a scrollable frame inside the existing frame to display contents
scrollable_frame = ctk.CTkScrollableFrame(frame, width=1280, height=720, corner_radius=0, fg_color="transparent")
scrollable_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")

# Add widgets to the scrollable frame
create_labels()

# Start the main event loop
app.mainloop()
