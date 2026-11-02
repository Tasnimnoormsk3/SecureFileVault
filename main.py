
import os
import customtkinter as ctk
from tkinter import filedialog

from password_manager import (
    is_vault_initialized,
    create_vault,
    unlock_vault
)


# --------------------------------------------------
# APP APPEARANCE
# --------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# --------------------------------------------------
# MAIN WINDOW
# --------------------------------------------------

app = ctk.CTk()
app.title("Secure File Vault")
app.geometry("700x650")
app.resizable(False, False)


# --------------------------------------------------
# GLOBAL VARIABLES
# --------------------------------------------------

selected_file = None
vault_key = None


# --------------------------------------------------
# FUNCTION TO SELECT A FILE
# --------------------------------------------------

def select_file():
    global selected_file

    file_path = filedialog.askopenfilename()

    if file_path:
        selected_file = file_path

        # Show only the filename instead of the full path
        file_label.configure(
            text=f"Selected File: {os.path.basename(file_path)}"
        )

        status_label.configure(
            text="Status: File selected successfully"
        )


# --------------------------------------------------
# FUNCTION TO REMOVE SELECTED FILE
# --------------------------------------------------

def remove_file():
    global selected_file

    selected_file = None

    file_label.configure(
        text="No file selected"
    )

    status_label.configure(
        text="Status: File removed"
    )


# --------------------------------------------------
# MASTER PASSWORD / ARGON2ID
# --------------------------------------------------

def handle_unlock():
    global vault_key

    password = password_entry.get()

    # Check if the field is empty
    if not password:
        status_label.configure(
            text="Status: Please enter a master password"
        )
        return

    try:

        # --------------------------------------------------
        # FIRST TIME THE VAULT IS USED
        # --------------------------------------------------

        if not is_vault_initialized():

            vault_key = create_vault(password)

            status_label.configure(
                text="Status: Master password created. Vault unlocked."
            )

        # --------------------------------------------------
        # VAULT ALREADY EXISTS
        # --------------------------------------------------

        else:

            vault_key = unlock_vault(password)

            # Wrong password
            if vault_key is None:

                status_label.configure(
                    text="Status: Incorrect master password"
                )

                password_entry.delete(0, "end")
                return

            # Correct password
            status_label.configure(
                text="Status: Vault unlocked successfully"
            )

        # Clear the password from the visible field
        password_entry.delete(0, "end")

        # Enable protected functions
        encrypt_button.configure(state="normal")
        decrypt_button.configure(state="normal")
        verify_button.configure(state="normal")

        # Prevent the user from repeatedly unlocking
        unlock_button.configure(
            text="Vault Unlocked",
            state="disabled"
        )

    except ValueError as error:

        # Used when password does not satisfy requirements
        status_label.configure(
            text=f"Status: {error}"
        )

    except Exception as error:

        status_label.configure(
            text="Status: Unable to unlock the vault"
        )

        # Useful while developing/debugging
        print("Vault error:", error)


# --------------------------------------------------
# PLACEHOLDER ENCRYPT FUNCTION
# AES-256 will be added next
# --------------------------------------------------

def encrypt_file():

    if vault_key is None:
        status_label.configure(
            text="Status: Unlock the vault first"
        )
        return

    if selected_file is None:
        status_label.configure(
            text="Status: Please select a file first"
        )
        return

    status_label.configure(
        text="Status: AES-256 encryption will be implemented next"
    )


# --------------------------------------------------
# PLACEHOLDER DECRYPT FUNCTION
# --------------------------------------------------

def decrypt_file():

    if vault_key is None:
        status_label.configure(
            text="Status: Unlock the vault first"
        )
        return

    if selected_file is None:
        status_label.configure(
            text="Status: Please select an encrypted file first"
        )
        return

    status_label.configure(
        text="Status: File decryption will be implemented next"
    )


# --------------------------------------------------
# PLACEHOLDER INTEGRITY FUNCTION
# SHA-256 will be added later
# --------------------------------------------------

def verify_integrity():

    if vault_key is None:
        status_label.configure(
            text="Status: Unlock the vault first"
        )
        return

    if selected_file is None:
        status_label.configure(
            text="Status: Please select a file first"
        )
        return

    status_label.configure(
        text="Status: SHA-256 integrity verification will be implemented next"
    )


# --------------------------------------------------
# TITLE
# --------------------------------------------------

title = ctk.CTkLabel(
    app,
    text="SECURE FILE VAULT",
    font=("Arial", 28, "bold")
)

title.pack(
    pady=(30, 20)
)


# --------------------------------------------------
# MASTER PASSWORD LABEL
# --------------------------------------------------

password_label = ctk.CTkLabel(
    app,
    text="Master Password",
    font=("Arial", 16)
)

password_label.pack(
    pady=(5, 5)
)


# --------------------------------------------------
# MASTER PASSWORD INPUT
# --------------------------------------------------

password_entry = ctk.CTkEntry(
    app,
    width=350,
    height=40,
    show="*",
    placeholder_text="Enter master password"
)

password_entry.pack(
    pady=10
)


# --------------------------------------------------
# CREATE / UNLOCK VAULT BUTTON
# --------------------------------------------------

unlock_button = ctk.CTkButton(
    app,
    text="Create / Unlock Vault",
    width=200,
    command=handle_unlock
)

unlock_button.pack(
    pady=5
)


# --------------------------------------------------
# SELECTED FILE LABEL
# --------------------------------------------------

file_label = ctk.CTkLabel(
    app,
    text="No file selected",
    wraplength=550
)

file_label.pack(
    pady=20
)


# --------------------------------------------------
# ADD FILE BUTTON
# --------------------------------------------------

add_button = ctk.CTkButton(
    app,
    text="Add File",
    width=200,
    command=select_file
)

add_button.pack(
    pady=6
)


# --------------------------------------------------
# ENCRYPT BUTTON
# Disabled until master password is verified
# --------------------------------------------------

encrypt_button = ctk.CTkButton(
    app,
    text="Encrypt",
    width=200,
    state="disabled",
    command=encrypt_file
)

encrypt_button.pack(
    pady=6
)


# --------------------------------------------------
# DECRYPT BUTTON
# --------------------------------------------------

decrypt_button = ctk.CTkButton(
    app,
    text="Decrypt",
    width=200,
    state="disabled",
    command=decrypt_file
)

decrypt_button.pack(
    pady=6
)


# --------------------------------------------------
# VERIFY INTEGRITY BUTTON
# --------------------------------------------------

verify_button = ctk.CTkButton(
    app,
    text="Verify Integrity",
    width=200,
    state="disabled",
    command=verify_integrity
)

verify_button.pack(
    pady=6
)


# --------------------------------------------------
# REMOVE FILE BUTTON
# --------------------------------------------------

remove_button = ctk.CTkButton(
    app,
    text="Remove File",
    width=200,
    command=remove_file
)

remove_button.pack(
    pady=6
)


# --------------------------------------------------
# STATUS LABEL
# --------------------------------------------------

status_label = ctk.CTkLabel(
    app,
    text="Status: Ready",
    font=("Arial", 14),
    wraplength=600
)

status_label.pack(
    pady=20
)


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

app.mainloop()