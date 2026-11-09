
import os
import customtkinter as ctk

from tkinter import (
    filedialog,
    messagebox
)

from password_manager import (
    is_vault_initialized,
    create_vault,
    unlock_vault
)

from crypto import (
    encrypt_file_aes,
    decrypt_file_aes
)

from integrity import (
    create_integrity_record,
    verify_integrity_record
)

from file_manager import (
    ensure_storage_directories,
    store_encrypted_file,
    store_retrieved_file,
    VAULT_DIR
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
app.geometry("700x780")
app.resizable(False, False)


# --------------------------------------------------
# GLOBAL VARIABLES
# --------------------------------------------------

selected_file = None
vault_key = None


# Create storage folders automatically
ensure_storage_directories()


# --------------------------------------------------
# SELECT NORMAL FILE
# --------------------------------------------------

def select_file():
    global selected_file

    file_path = filedialog.askopenfilename(
        title="Select a File"
    )

    if file_path:

        selected_file = file_path

        file_label.configure(
            text=(
                f"Selected File: "
                f"{os.path.basename(file_path)}"
            )
        )

        status_label.configure(
            text="Status: File selected successfully"
        )


# --------------------------------------------------
# SELECT FILE FROM SECURE VAULT
# --------------------------------------------------

def select_vault_file():
    global selected_file

    if vault_key is None:

        status_label.configure(
            text="Status: Unlock the vault first"
        )

        return

    file_path = filedialog.askopenfilename(
        initialdir=VAULT_DIR,
        title="Select a Protected Vault File",
        filetypes=[
            (
                "Secure File Vault Files",
                "*.vault"
            )
        ]
    )

    if file_path:

        selected_file = file_path

        file_label.configure(
            text=(
                f"Selected Vault File: "
                f"{os.path.basename(file_path)}"
            )
        )

        status_label.configure(
            text="Status: Vault file selected successfully"
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

        # ------------------------------------------
        # FIRST TIME USING THE VAULT
        # ------------------------------------------

        if not is_vault_initialized():

            vault_key = create_vault(
                password
            )

            status_label.configure(
                text=(
                    "Status: Master password created. "
                    "Vault unlocked."
                )
            )

        # ------------------------------------------
        # EXISTING VAULT
        # ------------------------------------------

        else:

            vault_key = unlock_vault(
                password
            )

            # Incorrect password
            if vault_key is None:

                status_label.configure(
                    text="Status: Incorrect master password"
                )

                password_entry.delete(
                    0,
                    "end"
                )

                return

            status_label.configure(
                text="Status: Vault unlocked successfully"
            )

        # Clear password from GUI
        password_entry.delete(
            0,
            "end"
        )

        # Enable protected functionality
        encrypt_button.configure(
            state="normal"
        )

        decrypt_button.configure(
            state="normal"
        )

        verify_button.configure(
            state="normal"
        )

        vault_files_button.configure(
            state="normal"
        )

        lock_button.configure(
            state="normal"
        )

        # Disable unlock button
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

        print(
            "Vault error:",
            error
        )


# --------------------------------------------------
# LOCK VAULT
# --------------------------------------------------

def lock_vault():
    global vault_key
    global selected_file

    # Remove the key from application state
    vault_key = None

    # Remove selected file
    selected_file = None

    # Clear password field
    password_entry.delete(
        0,
        "end"
    )

    file_label.configure(
        text="No file selected"
    )

    # Disable protected functions
    encrypt_button.configure(
        state="disabled"
    )

    decrypt_button.configure(
        state="disabled"
    )

    verify_button.configure(
        state="disabled"
    )

    vault_files_button.configure(
        state="disabled"
    )

    lock_button.configure(
        state="disabled"
    )

    # Allow vault to be unlocked again
    unlock_button.configure(
        text="Create / Unlock Vault",
        state="normal"
    )

    status_label.configure(
        text="Status: Vault locked successfully"
    )


# --------------------------------------------------
# AES-256-GCM ENCRYPTION
# + SHA-256 INTEGRITY RECORD
# + VAULT STORAGE
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

    # Prevent already encrypted files from
    # being encrypted again.
    if selected_file.endswith(".vault"):

        status_label.configure(
            text="Status: Selected file is already encrypted"
        )

        return

    if not os.path.isfile(
        selected_file
    ):

        status_label.configure(
            text="Status: Selected file could not be found"
        )

        return

    try:

        # ------------------------------------------
        # AES-256-GCM ENCRYPTION
        # ------------------------------------------

        encrypted_path = encrypt_file_aes(
            selected_file,
            vault_key
        )

        # ------------------------------------------
        # MOVE INTO DEDICATED VAULT
        # ------------------------------------------

        encrypted_path = store_encrypted_file(
            encrypted_path
        )

        # ------------------------------------------
        # SHA-256 INTEGRITY BASELINE
        # ------------------------------------------

        create_integrity_record(
            encrypted_path
        )

        encrypted_name = os.path.basename(
            encrypted_path
        )

        status_label.configure(
            text=(
                "Status: File encrypted successfully "
                "and stored in vault: "
                f"{encrypted_name}"
            )
        )

    except FileNotFoundError:

        status_label.configure(
            text="Status: Selected file could not be found"
        )

    except Exception as error:

        status_label.configure(
            text=f"Status: Encryption failed: {error}"
        )

        print(
            "Encryption error:",
            error
        )


# --------------------------------------------------
# AES-256-GCM DECRYPTION
# + AUTOMATIC SHA-256 CHECK
# + RETRIEVED FILE STORAGE
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
            text=(
                "Status: Please select an "
                "encrypted file first"
            )
        )

        return

    if not selected_file.endswith(
        ".vault"
    ):

        status_label.configure(
            text=(
                "Status: Please select a valid "
                ".vault encrypted file"
            )
        )

        return

    if not os.path.isfile(
        selected_file
    ):

        status_label.configure(
            text="Status: Encrypted file could not be found"
        )

        return

    try:

        # ------------------------------------------
        # AUTOMATIC INTEGRITY CHECK
        # BEFORE DECRYPTION
        # ------------------------------------------

        try:

            verified, stored_hash, current_hash = (
                verify_integrity_record(
                    selected_file
                )
            )

        except FileNotFoundError as error:

            status_label.configure(
                text=(
                    "Status: Decryption blocked - "
                    f"{error}"
                )
            )

            return

        if not verified:

            status_label.configure(
                text=(
                    "Status: Decryption blocked - "
                    "integrity check failed. "
                    "File may have been modified."
                )
            )

            return

        # ------------------------------------------
        # AES-256-GCM DECRYPTION
        # ------------------------------------------

        decrypted_path = decrypt_file_aes(
            selected_file,
            vault_key
        )

        # ------------------------------------------
        # MOVE INTO RETRIEVED FILES FOLDER
        # ------------------------------------------

        decrypted_path = store_retrieved_file(
            decrypted_path
        )

        decrypted_name = os.path.basename(
            decrypted_path
        )

        status_label.configure(
            text=(
                "Status: File decrypted successfully "
                "and saved to retrieved files: "
                f"{decrypted_name}"
            )
        )

    except ValueError as error:

        status_label.configure(
            text=f"Status: Decryption failed: {error}"
        )

    except Exception as error:

        status_label.configure(
            text="Status: Decryption failed"
        )

        print(
            "Decryption error:",
            error
        )


# --------------------------------------------------
# SHA-256 INTEGRITY VERIFICATION
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

    try:

        verified, stored_hash, current_hash = (
            verify_integrity_record(
                selected_file
            )
        )

        # ------------------------------------------
        # FILE HAS NOT CHANGED
        # ------------------------------------------

        if verified:

            status_label.configure(
                text=(
                    "Status: Integrity verified. "
                    "File has not been modified."
                )
            )

        # ------------------------------------------
        # FILE WAS MODIFIED
        # ------------------------------------------

        else:

            status_label.configure(
                text=(
                    "Status: INTEGRITY CHECK FAILED - "
                    "File may have been modified."
                )
            )

    except FileNotFoundError as error:

        status_label.configure(
            text=f"Status: {error}"
        )

    except ValueError as error:

        status_label.configure(
            text=f"Status: Integrity error: {error}"
        )

    except Exception as error:

        status_label.configure(
            text="Status: Unable to verify file integrity"
        )

        print(
            "Integrity verification error:",
            error
        )


# --------------------------------------------------
# REMOVE FILE / REMOVE FROM SELECTION
# --------------------------------------------------

def remove_file():
    global selected_file

    # Nothing selected
    if selected_file is None:

        status_label.configure(
            text="Status: No file is currently selected"
        )

        return

    selected_path = os.path.abspath(
        selected_file
    )

    vault_path = os.path.abspath(
        VAULT_DIR
    )

    try:

        inside_vault = (
            os.path.commonpath(
                [
                    selected_path,
                    vault_path
                ]
            )
            == vault_path
        )

    except ValueError:

        inside_vault = False

    # ----------------------------------------------
    # PROTECTED FILE INSIDE VAULT
    # ----------------------------------------------

    if (
        inside_vault
        and selected_file.endswith(".vault")
    ):

        if vault_key is None:

            status_label.configure(
                text=(
                    "Status: Unlock the vault before "
                    "removing protected files"
                )
            )

            return

        filename = os.path.basename(
            selected_file
        )

        confirmed = messagebox.askyesno(
            "Remove Protected File",
            (
                "Are you sure you want to remove "
                f"{filename} from the vault?"
            )
        )

        # User cancelled
        if not confirmed:

            status_label.configure(
                text="Status: File removal cancelled"
            )

            return

        try:

            # Integrity file associated with the
            # selected vault file
            integrity_path = (
                selected_file
                + ".sha256"
            )

            # Remove encrypted file
            os.remove(
                selected_file
            )

            # Remove SHA-256 record
            if os.path.exists(
                integrity_path
            ):

                os.remove(
                    integrity_path
                )

            selected_file = None

            file_label.configure(
                text="No file selected"
            )

            status_label.configure(
                text=(
                    "Status: Protected file removed "
                    "from vault"
                )
            )

        except Exception as error:

            status_label.configure(
                text=(
                    "Status: Unable to remove file: "
                    f"{error}"
                )
            )

    # ----------------------------------------------
    # NORMAL FILE
    #
    # Never delete the user's original file.
    # Only clear it from the GUI selection.
    # ----------------------------------------------

    else:

        selected_file = None

        file_label.configure(
            text="No file selected"
        )

        status_label.configure(
            text="Status: File removed from selection"
        )


# --------------------------------------------------
# TITLE
# --------------------------------------------------

title = ctk.CTkLabel(
    app,
    text="SECURE FILE VAULT",
    font=(
        "Arial",
        28,
        "bold"
    )
)

title.pack(
    pady=(25, 15)
)


# --------------------------------------------------
# MASTER PASSWORD LABEL
# --------------------------------------------------

password_label = ctk.CTkLabel(
    app,
    text="Master Password",
    font=(
        "Arial",
        16
    )
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
    pady=8
)


# --------------------------------------------------
# CREATE / UNLOCK VAULT
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
# LOCK VAULT
# --------------------------------------------------

lock_button = ctk.CTkButton(
    app,
    text="Lock Vault",
    width=200,
    state="disabled",
    command=lock_vault
)

lock_button.pack(
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
    pady=15
)


# --------------------------------------------------
# ADD FILE
# --------------------------------------------------

add_button = ctk.CTkButton(
    app,
    text="Add File",
    width=200,
    command=select_file
)

add_button.pack(
    pady=5
)


# --------------------------------------------------
# VIEW VAULT FILES
# --------------------------------------------------

vault_files_button = ctk.CTkButton(
    app,
    text="View Vault Files",
    width=200,
    state="disabled",
    command=select_vault_file
)

vault_files_button.pack(
    pady=5
)


# --------------------------------------------------
# ENCRYPT
# --------------------------------------------------

encrypt_button = ctk.CTkButton(
    app,
    text="Encrypt",
    width=200,
    state="disabled",
    command=encrypt_file
)

encrypt_button.pack(
    pady=5
)


# --------------------------------------------------
# DECRYPT
# --------------------------------------------------

decrypt_button = ctk.CTkButton(
    app,
    text="Decrypt",
    width=200,
    state="disabled",
    command=decrypt_file
)

decrypt_button.pack(
    pady=5
)


# --------------------------------------------------
# VERIFY INTEGRITY
# --------------------------------------------------

verify_button = ctk.CTkButton(
    app,
    text="Verify Integrity",
    width=200,
    state="disabled",
    command=verify_integrity
)

verify_button.pack(
    pady=5
)


# --------------------------------------------------
# REMOVE FILE
# --------------------------------------------------

remove_button = ctk.CTkButton(
    app,
    text="Remove File",
    width=200,
    command=remove_file
)

remove_button.pack(
    pady=5
)


# --------------------------------------------------
# STATUS
# --------------------------------------------------

status_label = ctk.CTkLabel(
    app,
    text="Status: Ready",
    font=(
        "Arial",
        14
    ),
    wraplength=620
)

status_label.pack(
    pady=20
)


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

app.mainloop()