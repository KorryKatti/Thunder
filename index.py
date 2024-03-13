import customtkinter as ctk

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

def quit(window):
    window.destroy()    

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
label = ctk.CTkLabel(scrollable_frame, text="This is the content frame")
label.pack()

# Start the main event loop
app.mainloop()
