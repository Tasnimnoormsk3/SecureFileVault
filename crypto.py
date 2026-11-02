
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


# File identifier so the program can recognise
# files created by this Secure File Vault.
FILE_HEADER = b"SFV1"

# AES-GCM commonly uses a 12-byte nonce.
NONCE_SIZE = 12


def validate_key(key):
    """
    Confirm that the encryption key is 256 bits.
    """

    if not isinstance(key, bytes):
        raise ValueError("Encryption key must be bytes.")

    if len(key) != 32:
        raise ValueError(
            "AES-256 requires a 32-byte encryption key."
        )


def encrypt_file_aes(file_path, key):
    """
    Encrypt a file using AES-256-GCM.

    File format:
    [SFV1 HEADER][12-BYTE NONCE][CIPHERTEXT + AUTH TAG]
    """

    validate_key(key)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            "The selected file does not exist."
        )

    # Read original file
    with open(file_path, "rb") as file:
        plaintext = file.read()

    # Generate a new random nonce for every encryption
    nonce = os.urandom(NONCE_SIZE)

    aesgcm = AESGCM(key)

    # AES-GCM automatically includes authentication
    ciphertext = aesgcm.encrypt(
        nonce,
        plaintext,
        None
    )

    # Do not overwrite the original file
    encrypted_path = file_path + ".vault"

    with open(encrypted_path, "wb") as encrypted_file:
        encrypted_file.write(FILE_HEADER)
        encrypted_file.write(nonce)
        encrypted_file.write(ciphertext)

    return encrypted_path


def decrypt_file_aes(file_path, key):
    """
    Decrypt a .vault file created by this application.
    """

    validate_key(key)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            "The selected encrypted file does not exist."
        )

    with open(file_path, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    minimum_size = len(FILE_HEADER) + NONCE_SIZE + 16

    if len(encrypted_data) < minimum_size:
        raise ValueError(
            "Invalid or damaged encrypted file."
        )

    # Verify our file header
    header = encrypted_data[:len(FILE_HEADER)]

    if header != FILE_HEADER:
        raise ValueError(
            "This file was not created by Secure File Vault."
        )

    nonce_start = len(FILE_HEADER)
    nonce_end = nonce_start + NONCE_SIZE

    nonce = encrypted_data[
        nonce_start:nonce_end
    ]

    ciphertext = encrypted_data[
        nonce_end:
    ]

    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(
            nonce,
            ciphertext,
            None
        )

    except InvalidTag:
        raise ValueError(
            "Decryption failed. Wrong password or file has been modified."
        )

    # Work out a safe output filename
    if file_path.endswith(".vault"):
        original_path = file_path[:-6]
    else:
        original_path = file_path

    root, extension = os.path.splitext(
        original_path
    )

    decrypted_path = (
        f"{root}_decrypted{extension}"
    )

    with open(decrypted_path, "wb") as decrypted_file:
        decrypted_file.write(plaintext)

    return decrypted_path