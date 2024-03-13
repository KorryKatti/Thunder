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
    data_dir = "data"
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            with open(os.path.join(data_dir, filename), "r") as f:
                app_data = json.load(f)

                # Create a label for the application name
                name_label = ctk.CTkLabel(scrollable_frame, text=app_data.get("name", "Unknown"))
                name_label.pack()

                # Display the application icon
                icon_url = app_data.get("icon_url", "")
                if icon_url:
                    # Download the image from URL
                    icon_image = download_image(icon_url)

                    if icon_image:
                        # Create a CTkImage object
                        ct_image = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(30, 30))

                        # Create a label to display the image
                        image_label = ctk.CTkLabel(scrollable_frame, image=ct_image, text="")
                        image_label.pack()

                # Create a button for downloading the application
                download_button = ctk.CTkButton(scrollable_frame, text="Download")
                download_button.pack()

                # Create a separator line
                separator = ctk.CTkLabel(scrollable_frame, text="--------------------------")
                separator.pack()

# Create the main application window
app = ctk.CTk()
app.geometry("800x600")
app.resizable(True, True)
app.title("Thunder 🗲")

#functions for optionmenu
def quit(window):
    window.destroy()    

# Create a frame inside the main window for organizing widgets
frame = ctk.CTkFrame(app)
frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)  # Pack the frame to fill the window

# Define the callback function for the optionmenu
def optionmenu_callback(choice):
    print("Optionmenu dropdown clicked:", choice)
    if choice == "Quit":
        quit(app)

# Callback Function for Libmenu
def libmenu_callback():
    pass

# CallBack function for commenu
def commenu_callback():
    pass

# CallBack function for devmenu
def devmenu_callback():
    pass

# Create the optionmenu widget
optionmenu = ctk.CTkOptionMenu(frame, values=["Home", "Client Update", "Quit"],
                                         command=optionmenu_callback)
optionmenu.grid(row=0, column=1, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create the library menu widget
libmenu = ctk.CTkOptionMenu(frame, values=["Library", "Apps Update"],
                                         command=libmenu_callback)
libmenu.grid(row=0, column=2, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create the Commmunity Widget
commenu = ctk.CTkOptionMenu(frame, values=["Community", "Image Board", "Thunder Halls"],
                                         command=commenu_callback)
commenu.grid(row=0, column=3, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create DevBlogs Widget
devmenu = ctk.CTkOptionMenu(frame,values=["Dev Blog", "Changelogs"],
                                         command=devmenu_callback)
devmenu.grid(row=0, column=4, padx=10, pady=0, sticky=ctk.W)  # Align to the west (left)

# Create a scrollable frame inside the existing frame to display contents
scrollable_frame = ctk.CTkScrollableFrame(frame, width=750, height=750, corner_radius=0, fg_color="transparent")
scrollable_frame.grid(row=3, column=0, columnspan=33, sticky="nsew")

# Add widgets to the scrollable frame
create_labels()

# Start the main event loop
app.mainloop()
