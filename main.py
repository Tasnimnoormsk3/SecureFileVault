
import os
import customtkinter as ctk
from tkinter import filedialog

from password_manager import (
    is_vault_initialized,
    create_vault,
    unlock_vault
)

from crypto import (
    encrypt_file_aes,
    decrypt_file_aes
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
# SELECT FILE
# --------------------------------------------------

def select_file():
    global selected_file

    file_path = filedialog.askopenfilename()

    if file_path:
        selected_file = file_path

        file_label.configure(
            text=f"Selected File: {os.path.basename(file_path)}"
        )

        status_label.configure(
            text="Status: File selected successfully"
        )


# --------------------------------------------------
# REMOVE SELECTED FILE
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

    if not password:
        status_label.configure(
            text="Status: Please enter a master password"
        )
        return

    try:

        # FIRST TIME USING THE VAULT
        if not is_vault_initialized():

            vault_key = create_vault(password)

            status_label.configure(
                text="Status: Master password created. Vault unlocked."
            )

        # EXISTING VAULT
        else:

            vault_key = unlock_vault(password)

            if vault_key is None:

                status_label.configure(
                    text="Status: Incorrect master password"
                )

                password_entry.delete(0, "end")
                return

            status_label.configure(
                text="Status: Vault unlocked successfully"
            )

        # Clear password field after successful use
        password_entry.delete(0, "end")

        # Enable security functions
        encrypt_button.configure(state="normal")
        decrypt_button.configure(state="normal")
        verify_button.configure(state="normal")

        unlock_button.configure(
            text="Vault Unlocked",
            state="disabled"
        )

    except ValueError as error:

        status_label.configure(
            text=f"Status: {error}"
        )

    except Exception as error:

        status_label.configure(
            text="Status: Unable to unlock the vault"
        )

        print("Vault error:", error)


# --------------------------------------------------
# AES-256 ENCRYPTION
# --------------------------------------------------

def encrypt_file():
    global selected_file

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

    # Prevent accidentally encrypting an already encrypted file
    if selected_file.endswith(".vault"):
        status_label.configure(
            text="Status: Selected file is already encrypted"
        )
        return

    try:

        encrypted_path = encrypt_file_aes(
            selected_file,
            vault_key
        )

        encrypted_name = os.path.basename(
            encrypted_path
        )

        status_label.configure(
            text=f"Status: File encrypted successfully: {encrypted_name}"
        )

    except FileNotFoundError:

        status_label.configure(
            text="Status: Selected file could not be found"
        )

    except Exception as error:

        status_label.configure(
            text=f"Status: Encryption failed: {error}"
        )

        print("Encryption error:", error)


# --------------------------------------------------
# AES-256 DECRYPTION
# --------------------------------------------------

def decrypt_file():
    global selected_file

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

    # Only allow Secure File Vault encrypted files
    if not selected_file.endswith(".vault"):
        status_label.configure(
            text="Status: Please select a valid .vault encrypted file"
        )
        return

    try:

        decrypted_path = decrypt_file_aes(
            selected_file,
            vault_key
        )

        decrypted_name = os.path.basename(
            decrypted_path
        )

        status_label.configure(
            text=f"Status: File decrypted successfully: {decrypted_name}"
        )

    except FileNotFoundError:

        status_label.configure(
            text="Status: Encrypted file could not be found"
        )

    except ValueError as error:

        status_label.configure(
            text=f"Status: Decryption failed: {error}"
        )

    except Exception as error:

        status_label.configure(
            text="Status: Decryption failed"
        )

        print("Decryption error:", error)


# --------------------------------------------------
# SHA-256 INTEGRITY
# Will be implemented in the next milestone
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