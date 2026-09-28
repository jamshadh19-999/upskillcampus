"""Encryption helpers.

How it works
------------
1. The user's *master password* is never stored.
2. A random *salt* is stored in the database. PBKDF2-HMAC-SHA256 combines the
   master password + salt (hundreds of thousands of rounds) into a 32-byte key.
3. That key drives Fernet (AES-128-CBC + HMAC-SHA256), which encrypts and
   authenticates every secret we store. Tampered or wrongly-decrypted data is
   detected automatically.
"""

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import config

# A known value we encrypt at vault creation. If we can decrypt it later, the
# master password entered is correct.
VERIFIER_PLAINTEXT = "password-manager-vault-ok"


class CryptoError(Exception):
    """Raised when data cannot be decrypted (wrong key or corrupted data)."""


def generate_salt() -> bytes:
    """Return a fresh random salt."""
    return os.urandom(config.SALT_SIZE)


def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from the master password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=config.KDF_ITERATIONS,
    )
    raw_key = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(raw_key)


class Cipher:
    """Small wrapper around Fernet that works with plain strings."""

    def __init__(self, key: bytes):
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise CryptoError("Could not decrypt data (wrong key or corrupted).") from exc
