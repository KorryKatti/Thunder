import customtkinter as ctk
import subprocess
import os
import json
import requests
from PIL import Image
from io import BytesIO

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

    # Fetch README content from the repository URL
    repo_url = app_data.get("repo_url", "")
    if repo_url:
        try:
            response = requests.get(repo_url + "/blob/main/README.md")
            response.raise_for_status()
            readme_content = response.text
            # Create a label for displaying README content
            readme_label = ctk.CTkLabel(details_frame, text=readme_content, wraplength=700)
            readme_label.pack(side=ctk.TOP, padx=10, pady=5)
        except Exception as e:
            print(f"Error fetching README content: {e}")

    # Create a button for downloading the application
    download_button = ctk.CTkButton(details_frame, text="Download", command=lambda: download_app(app_data))
    download_button.pack(side=ctk.TOP, padx=10, pady=5)

    # Create a separator line
    separator = ctk.CTkLabel(scrollable_frame, text="--------------------------")
    separator.pack(fill=ctk.X, padx=10, pady=5)


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
def libmenu_callback():
    pass

# CallBack function for commenu
def commenu_callback():
    pass

# CallBack function for devmenu
def devmenu_callback():
    pass

#functions for optionmenu
def quit(window):
    window.destroy()    

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
