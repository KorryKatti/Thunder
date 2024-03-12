import customtkinter

# Set the appearance mode and default color theme
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

# Create the main application window
app = customtkinter.CTk()
app.geometry("400x240")
app.resizable(True, True)
app.title("Thunder 🗲")

# Create a frame inside the main window for organizing widgets
frame = customtkinter.CTkFrame(app)
frame.pack(fill=customtkinter.BOTH, expand=True, padx=20, pady=20)  # Pack the frame to fill the window

# Add widgets to the frame
label = customtkinter.CTkLabel(frame, text="This is a label inside the frame")
label.grid(row=0, column=0, padx=10, pady=10, sticky=customtkinter.W)  # Align to the west (left)

button = customtkinter.CTkButton(frame, text="Click me")
button.grid(row=0, column=1, padx=10, pady=10, sticky=customtkinter.W)  # Align to the west (left)

# Start the main event loop
app.mainloop()
