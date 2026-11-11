
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

from audit_logger import (
    ensure_audit_log,
    log_event,
    get_audit_log_text
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

app.title(
    "Secure File Vault"
)

app.geometry(
    "700x830"
)

app.resizable(
    False,
    False
)


# --------------------------------------------------
# GLOBAL VARIABLES
# --------------------------------------------------

selected_file = None
vault_key = None


# Create required local folders
ensure_storage_directories()
ensure_audit_log()


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
                "Selected File: "
                f"{os.path.basename(file_path)}"
            )
        )

        status_label.configure(
            text="Status: File selected successfully"
        )


# --------------------------------------------------
# SELECT VAULT FILE
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
                "Selected Vault File: "
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

        # First-time setup
        if not is_vault_initialized():

            vault_key = create_vault(
                password
            )

            log_event(
                "VAULT_INITIALIZED",
                "SUCCESS",
                details="Master password configured"
            )

            log_event(
                "VAULT_UNLOCK",
                "SUCCESS"
            )

            status_label.configure(
                text=(
                    "Status: Master password created. "
                    "Vault unlocked."
                )
            )

        # Existing vault
        else:

            vault_key = unlock_vault(
                password
            )

            if vault_key is None:

                log_event(
                    "VAULT_UNLOCK",
                    "FAILED",
                    details="Incorrect password"
                )

                status_label.configure(
                    text="Status: Incorrect master password"
                )

                password_entry.delete(
                    0,
                    "end"
                )

                return

            log_event(
                "VAULT_UNLOCK",
                "SUCCESS"
            )

            status_label.configure(
                text="Status: Vault unlocked successfully"
            )

        password_entry.delete(
            0,
            "end"
        )

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

        activity_log_button.configure(
            state="normal"
        )

        lock_button.configure(
            state="normal"
        )

        unlock_button.configure(
            text="Vault Unlocked",
            state="disabled"
        )

    except ValueError as error:

        log_event(
            "VAULT_UNLOCK",
            "FAILED",
            details=str(error)
        )

        status_label.configure(
            text=f"Status: {error}"
        )

    except Exception as error:

        log_event(
            "VAULT_UNLOCK",
            "ERROR",
            details="Unexpected vault error"
        )

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

    log_event(
        "VAULT_LOCK",
        "SUCCESS"
    )

    vault_key = None
    selected_file = None

    password_entry.delete(
        0,
        "end"
    )

    file_label.configure(
        text="No file selected"
    )

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

    activity_log_button.configure(
        state="disabled"
    )

    lock_button.configure(
        state="disabled"
    )

    unlock_button.configure(
        text="Create / Unlock Vault",
        state="normal"
    )

    status_label.configure(
        text="Status: Vault locked successfully"
    )


# --------------------------------------------------
# ENCRYPT FILE
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

    if selected_file.endswith(
        ".vault"
    ):

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

    original_file = selected_file

    try:

        encrypted_path = encrypt_file_aes(
            selected_file,
            vault_key
        )

        encrypted_path = store_encrypted_file(
            encrypted_path
        )

        create_integrity_record(
            encrypted_path
        )

        log_event(
            "FILE_ENCRYPT",
            "SUCCESS",
            file_path=original_file
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

    except Exception as error:

        log_event(
            "FILE_ENCRYPT",
            "FAILED",
            file_path=original_file,
            details=str(error)
        )

        status_label.configure(
            text=f"Status: Encryption failed: {error}"
        )


# --------------------------------------------------
# DECRYPT FILE
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

    vault_file = selected_file

    try:

        # Automatic integrity verification
        try:

            verified, stored_hash, current_hash = (
                verify_integrity_record(
                    selected_file
                )
            )

        except FileNotFoundError as error:

            log_event(
                "FILE_DECRYPT",
                "BLOCKED",
                file_path=vault_file,
                details="Integrity record missing"
            )

            status_label.configure(
                text=(
                    "Status: Decryption blocked - "
                    f"{error}"
                )
            )

            return

        if not verified:

            log_event(
                "FILE_DECRYPT",
                "BLOCKED",
                file_path=vault_file,
                details="Integrity verification failed"
            )

            log_event(
                "INTEGRITY_CHECK",
                "FAILED",
                file_path=vault_file,
                details="Possible file modification detected"
            )

            status_label.configure(
                text=(
                    "Status: Decryption blocked - "
                    "integrity check failed. "
                    "File may have been modified."
                )
            )

            return

        decrypted_path = decrypt_file_aes(
            selected_file,
            vault_key
        )

        decrypted_path = store_retrieved_file(
            decrypted_path
        )

        log_event(
            "FILE_DECRYPT",
            "SUCCESS",
            file_path=vault_file
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

        log_event(
            "FILE_DECRYPT",
            "FAILED",
            file_path=vault_file,
            details=str(error)
        )

        status_label.configure(
            text=f"Status: Decryption failed: {error}"
        )

    except Exception as error:

        log_event(
            "FILE_DECRYPT",
            "ERROR",
            file_path=vault_file
        )

        status_label.configure(
            text="Status: Decryption failed"
        )

        print(
            "Decryption error:",
            error
        )


# --------------------------------------------------
# VERIFY INTEGRITY
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

        if verified:

            log_event(
                "INTEGRITY_CHECK",
                "SUCCESS",
                file_path=selected_file
            )

            status_label.configure(
                text=(
                    "Status: Integrity verified. "
                    "File has not been modified."
                )
            )

        else:

            log_event(
                "INTEGRITY_CHECK",
                "FAILED",
                file_path=selected_file,
                details="Possible file modification detected"
            )

            status_label.configure(
                text=(
                    "Status: INTEGRITY CHECK FAILED - "
                    "File may have been modified."
                )
            )

    except FileNotFoundError as error:

        log_event(
            "INTEGRITY_CHECK",
            "FAILED",
            file_path=selected_file,
            details="Integrity record missing"
        )

        status_label.configure(
            text=f"Status: {error}"
        )

    except Exception as error:

        log_event(
            "INTEGRITY_CHECK",
            "ERROR",
            file_path=selected_file
        )

        status_label.configure(
            text="Status: Unable to verify file integrity"
        )

        print(
            "Integrity verification error:",
            error
        )


# --------------------------------------------------
# REMOVE FILE
# --------------------------------------------------

def remove_file():

    global selected_file

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

        if not confirmed:

            log_event(
                "FILE_REMOVE",
                "CANCELLED",
                file_path=selected_file
            )

            status_label.configure(
                text="Status: File removal cancelled"
            )

            return

        try:

            integrity_path = (
                selected_file
                + ".sha256"
            )

            log_file_path = selected_file

            os.remove(
                selected_file
            )

            if os.path.exists(
                integrity_path
            ):

                os.remove(
                    integrity_path
                )

            log_event(
                "FILE_REMOVE",
                "SUCCESS",
                file_path=log_file_path
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

            log_event(
                "FILE_REMOVE",
                "FAILED",
                file_path=selected_file,
                details=str(error)
            )

            status_label.configure(
                text=(
                    "Status: Unable to remove file: "
                    f"{error}"
                )
            )

    else:

        selected_file = None

        file_label.configure(
            text="No file selected"
        )

        status_label.configure(
            text="Status: File removed from selection"
        )


# --------------------------------------------------
# VIEW SECURITY ACTIVITY LOG
# --------------------------------------------------

def show_activity_log():

    if vault_key is None:

        status_label.configure(
            text="Status: Unlock the vault first"
        )

        return

    log_window = ctk.CTkToplevel(
        app
    )

    log_window.title(
        "Security Activity Log"
    )

    log_window.geometry(
        "850x500"
    )

    log_title = ctk.CTkLabel(
        log_window,
        text="SECURITY ACTIVITY LOG",
        font=(
            "Arial",
            22,
            "bold"
        )
    )

    log_title.pack(
        pady=20
    )

    log_textbox = ctk.CTkTextbox(
        log_window,
        width=800,
        height=390
    )

    log_textbox.pack(
        padx=20,
        pady=10
    )

    log_textbox.insert(
        "1.0",
        get_audit_log_text()
    )

    log_textbox.configure(
        state="disabled"
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
    pady=(25, 12)
)


# --------------------------------------------------
# PASSWORD
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
# UNLOCK
# --------------------------------------------------

unlock_button = ctk.CTkButton(
    app,
    text="Create / Unlock Vault",
    width=200,
    command=handle_unlock
)

unlock_button.pack(
    pady=4
)


# --------------------------------------------------
# LOCK
# --------------------------------------------------

lock_button = ctk.CTkButton(
    app,
    text="Lock Vault",
    width=200,
    state="disabled",
    command=lock_vault
)

lock_button.pack(
    pady=4
)


# --------------------------------------------------
# FILE LABEL
# --------------------------------------------------

file_label = ctk.CTkLabel(
    app,
    text="No file selected",
    wraplength=550
)

file_label.pack(
    pady=12
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
    pady=4
)


# --------------------------------------------------
# VIEW VAULT
# --------------------------------------------------

vault_files_button = ctk.CTkButton(
    app,
    text="View Vault Files",
    width=200,
    state="disabled",
    command=select_vault_file
)

vault_files_button.pack(
    pady=4
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
    pady=4
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
    pady=4
)


# --------------------------------------------------
# VERIFY
# --------------------------------------------------

verify_button = ctk.CTkButton(
    app,
    text="Verify Integrity",
    width=200,
    state="disabled",
    command=verify_integrity
)

verify_button.pack(
    pady=4
)


# --------------------------------------------------
# REMOVE
# --------------------------------------------------

remove_button = ctk.CTkButton(
    app,
    text="Remove File",
    width=200,
    command=remove_file
)

remove_button.pack(
    pady=4
)


# --------------------------------------------------
# ACTIVITY LOG
# --------------------------------------------------

activity_log_button = ctk.CTkButton(
    app,
    text="View Activity Log",
    width=200,
    state="disabled",
    command=show_activity_log
)

activity_log_button.pack(
    pady=4
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
    pady=16
)


# --------------------------------------------------
# START
# --------------------------------------------------

app.mainloop()