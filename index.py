import customtkinter

# Set the appearance mode and default color theme
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

# Create the main application window
app = customtkinter.CTk()
app.geometry("400x240")
app.resizable(True, True)
app.title("Thunder 🗲")

# Define the callback function for the optionmenu
def optionmenu_callback(choice):
    print("Optionmenu dropdown clicked:", choice)

# Create a frame inside the main window for organizing widgets
frame = customtkinter.CTkFrame(app)
frame.pack(fill=customtkinter.BOTH, expand=True, padx=20, pady=20)  # Pack the frame to fill the window

# Create the optionmenu widget
optionmenu = customtkinter.CTkOptionMenu(frame, values=["Home", "Check For Updates", "Quit"],
                                         command=optionmenu_callback)
optionmenu.grid(row=0, column=2, padx=10, pady=10, sticky=customtkinter.W)  # Align to the west (left)

# Create a new frame inside the existing frame to display contents
content_frame = customtkinter.CTkFrame(frame)
content_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")  # Span across all columns, fill horizontally

# Add widgets to the content frame
label = customtkinter.CTkLabel(content_frame, text="This is the content frame")
label.pack()

# Start the main event loop
app.mainloop()
