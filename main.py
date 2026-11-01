import customtkinter as ctk
from tkinter import filedialog

# App appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Main window
app = ctk.CTk()
app.title("Secure File Vault")
app.geometry("700x550")

selected_file = None


# Function to select a file
def select_file():
    global selected_file

    file_path = filedialog.askopenfilename()

    if file_path:
        selected_file = file_path
        import os
        file_label.configure(text=os.path.basename(file_path))
        status_label.configure(text="Status: File selected successfully")


# Function to remove selected file
def remove_file():
    global selected_file

    selected_file = None
    file_label.configure(text="No file selected")
    status_label.configure(text="Status: File removed")


# Title
title = ctk.CTkLabel(
    app,
    text="SECURE FILE VAULT",
    font=("Arial", 28, "bold")
)
title.pack(pady=(30, 20))


# Master password label
password_label = ctk.CTkLabel(
    app,
    text="Master Password",
    font=("Arial", 16)
)
password_label.pack(pady=(5, 5))


# Master password input
password_entry = ctk.CTkEntry(
    app,
    width=350,
    height=40,
    show="*",
    placeholder_text="Enter master password"
)
password_entry.pack(pady=10)


# Selected file label
file_label = ctk.CTkLabel(
    app,
    text="No file selected",
    wraplength=550
)
file_label.pack(pady=20)


# Add File button
add_button = ctk.CTkButton(
    app,
    text="Add File",
    width=200,
    command=select_file
)
add_button.pack(pady=6)


# Encrypt button
encrypt_button = ctk.CTkButton(
    app,
    text="Encrypt",
    width=200
)
encrypt_button.pack(pady=6)


# Decrypt button
decrypt_button = ctk.CTkButton(
    app,
    text="Decrypt",
    width=200
)
decrypt_button.pack(pady=6)


# Verify Integrity button
verify_button = ctk.CTkButton(
    app,
    text="Verify Integrity",
    width=200
)
verify_button.pack(pady=6)


# Remove File button
remove_button = ctk.CTkButton(
    app,
    text="Remove File",
    width=200,
    command=remove_file
)
remove_button.pack(pady=6)


# Status
status_label = ctk.CTkLabel(
    app,
    text="Status: Ready",
    font=("Arial", 14)
)
status_label.pack(pady=20)


# IMPORTANT: this must stay at the very bottom
app.mainloop()