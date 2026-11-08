
import os
import hashlib
import hmac


HASH_EXTENSION = ".sha256"
CHUNK_SIZE = 65536


def calculate_sha256(file_path):
    """
    Calculate the SHA-256 hash of a file.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            "The selected file does not exist."
        )

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:
            chunk = file.read(CHUNK_SIZE)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def create_integrity_record(file_path):
    """
    Create and save a SHA-256 hash for the file.
    """

    file_hash = calculate_sha256(file_path)

    integrity_path = file_path + HASH_EXTENSION

    with open(
        integrity_path,
        "w",
        encoding="utf-8"
    ) as integrity_file:

        integrity_file.write(file_hash)

    return integrity_path, file_hash


def verify_integrity_record(file_path):
    """
    Compare the current file hash with the
    previously stored SHA-256 hash.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            "The selected file does not exist."
        )

    integrity_path = file_path + HASH_EXTENSION

    if not os.path.isfile(integrity_path):
        raise FileNotFoundError(
            "No SHA-256 integrity record was found for this file."
        )

    with open(
        integrity_path,
        "r",
        encoding="utf-8"
    ) as integrity_file:

        stored_hash = integrity_file.read().strip()

    current_hash = calculate_sha256(file_path)

    hashes_match = hmac.compare_digest(
        stored_hash,
        current_hash
    )

    return hashes_match, stored_hash, current_hash