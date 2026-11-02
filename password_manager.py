
import os
import json
import base64

from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from argon2.exceptions import VerifyMismatchError, VerificationError


# Store configuration beside this Python file
CONFIG_FILE = os.path.join(
    os.path.dirname(__file__),
    "vault_config.json"
)

# Argon2id settings
TIME_COST = 3
MEMORY_COST = 65536   
PARALLELISM = 4
HASH_LENGTH = 32
SALT_LENGTH = 16


# Password verifier
password_hasher = PasswordHasher(
    time_cost=TIME_COST,
    memory_cost=MEMORY_COST,
    parallelism=PARALLELISM,
    hash_len=HASH_LENGTH,
    salt_len=SALT_LENGTH,
    type=Type.ID
)


def validate_master_password(password):
    """
    Basic password requirement.
    A longer password is preferred for the vault.
    """

    if len(password) < 12:
        return False, "Master password must contain at least 12 characters."

    return True, ""


def generate_salt():
    """
    Generate a random 16-byte salt.
    """

    return os.urandom(SALT_LENGTH)


def derive_key(password, salt):
    """
    Derive a 256-bit (32-byte) encryption key
    from the master password using Argon2id.
    """

    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=TIME_COST,
        memory_cost=MEMORY_COST,
        parallelism=PARALLELISM,
        hash_len=HASH_LENGTH,
        type=Type.ID
    )


def is_vault_initialized():
    """
    Check whether a master password
    has already been configured.
    """

    return os.path.exists(CONFIG_FILE)


def create_vault(password):
    """
    Create the initial master-password configuration.
    The actual password is never stored.
    """

    valid, message = validate_master_password(password)

    if not valid:
        raise ValueError(message)

    # Password hash used for future password verification
    password_hash = password_hasher.hash(password)

    # Separate salt used for encryption-key derivation
    key_salt = generate_salt()

    config = {
        "password_hash": password_hash,
        "key_salt": base64.b64encode(key_salt).decode("utf-8")
    }

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

    # Key exists only in memory
    return derive_key(password, key_salt)


def unlock_vault(password):
    """
    Verify the entered master password.

    If correct:
        Return the derived 256-bit encryption key.

    If incorrect:
        Return None.
    """

    if not is_vault_initialized():
        raise FileNotFoundError(
            "The vault has not been initialized."
        )

    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    try:
        password_hasher.verify(
            config["password_hash"],
            password
        )

    except (VerifyMismatchError, VerificationError):
        return None

    key_salt = base64.b64decode(
        config["key_salt"]
    )

    return derive_key(password, key_salt)