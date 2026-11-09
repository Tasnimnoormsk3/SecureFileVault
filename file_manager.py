
import os
import shutil


# --------------------------------------------------
# STORAGE LOCATIONS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VAULT_DIR = os.path.join(
    BASE_DIR,
    "vault_files"
)

RETRIEVED_DIR = os.path.join(
    BASE_DIR,
    "retrieved_files"
)


# --------------------------------------------------
# CREATE STORAGE FOLDERS
# --------------------------------------------------

def ensure_storage_directories():
    """
    Create the vault and retrieved-file folders
    if they do not already exist.
    """

    os.makedirs(
        VAULT_DIR,
        exist_ok=True
    )

    os.makedirs(
        RETRIEVED_DIR,
        exist_ok=True
    )


# --------------------------------------------------
# GENERATE UNIQUE FILE NAME
# --------------------------------------------------

def get_unique_path(folder, filename):
    """
    Prevent existing files from being overwritten.
    """

    destination = os.path.join(
        folder,
        filename
    )

    if not os.path.exists(destination):
        return destination

    name, extension = os.path.splitext(
        filename
    )

    counter = 1

    while True:

        new_filename = (
            f"{name}_{counter}{extension}"
        )

        destination = os.path.join(
            folder,
            new_filename
        )

        if not os.path.exists(destination):
            return destination

        counter += 1


# --------------------------------------------------
# STORE ENCRYPTED FILE
# --------------------------------------------------

def store_encrypted_file(file_path):
    """
    Move an encrypted file into the vault folder.
    """

    ensure_storage_directories()

    filename = os.path.basename(
        file_path
    )

    destination = get_unique_path(
        VAULT_DIR,
        filename
    )

    shutil.move(
        file_path,
        destination
    )

    return destination


# --------------------------------------------------
# STORE DECRYPTED FILE
# --------------------------------------------------

def store_retrieved_file(file_path):
    """
    Move a decrypted file into the retrieved-files
    folder.
    """

    ensure_storage_directories()

    filename = os.path.basename(
        file_path
    )

    destination = get_unique_path(
        RETRIEVED_DIR,
        filename
    )

    shutil.move(
        file_path,
        destination
    )

    return destination


# --------------------------------------------------
# LIST VAULT FILES
# --------------------------------------------------

def get_vault_files():
    """
    Return all .vault files currently stored.
    """

    ensure_storage_directories()

    files = []

    for filename in os.listdir(
        VAULT_DIR
    ):

        if filename.endswith(".vault"):

            files.append(
                os.path.join(
                    VAULT_DIR,
                    filename
                )
            )

    return files
