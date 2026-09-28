"""PasswordManager: the one class the UI talks to.

It combines the database (storage) with the cipher (encryption) and enforces
the rules: the vault must be unlocked before any secret can be read or written.
"""

from dataclasses import dataclass
from typing import Optional

import config
from core import crypto
from core.crypto import Cipher, CryptoError
from core.database import Database


# ------------------------------------------------------------------ exceptions
class VaultLockedError(Exception):
    """Raised when an action needs the vault to be unlocked first."""


class InvalidMasterPasswordError(Exception):
    """Raised when the master password is wrong."""


class WeakMasterPasswordError(ValueError):
    """Raised when a new master password does not meet the rules."""


class EntryNotFoundError(KeyError):
    """Raised when an entry id does not exist."""


class ValidationError(ValueError):
    """Raised when entry fields are invalid (e.g. empty service name)."""


# ----------------------------------------------------------------------- model
@dataclass
class Entry:
    id: int
    service: str
    username: str
    password: Optional[str]  # None in list views - only filled by get_entry()
    notes: str
    created_at: str
    updated_at: str


# --------------------------------------------------------------------- manager
class PasswordManager:
    def __init__(self, db_path=config.DB_PATH):
        self._db = Database(db_path)
        self._cipher: Optional[Cipher] = None

    # -------------------------------------------------------------- vault state
    @property
    def is_initialized(self) -> bool:
        """True once a master password has been created."""
        return self._db.get_meta("salt") is not None

    @property
    def is_unlocked(self) -> bool:
        return self._cipher is not None

    def create_vault(self, master_password: str) -> None:
        """First-time setup: choose a master password and unlock the vault."""
        if self.is_initialized:
            raise RuntimeError("A vault already exists.")
        self._validate_master_password(master_password)

        salt = crypto.generate_salt()
        cipher = Cipher(crypto.derive_key(master_password, salt))
        verifier = cipher.encrypt(crypto.VERIFIER_PLAINTEXT).encode("ascii")
        self._db.replace_key_material(salt, verifier)
        self._cipher = cipher

    def unlock(self, master_password: str) -> None:
        """Unlock the vault or raise InvalidMasterPasswordError."""
        self._cipher = self._verified_cipher(master_password)

    def lock(self) -> None:
        """Forget the key. (Python can't guarantee wiping memory, but this drops
        our only reference to it.)"""
        self._cipher = None

    def change_master_password(self, old_password: str, new_password: str) -> None:
        """Re-encrypt every entry under a new master password (all-or-nothing)."""
        old_cipher = self._verified_cipher(old_password)
        self._validate_master_password(new_password)

        new_salt = crypto.generate_salt()
        new_cipher = Cipher(crypto.derive_key(new_password, new_salt))

        reencrypted = []
        for row in self._db.all_secrets():
            password = old_cipher.decrypt(row["password_enc"])
            notes = old_cipher.decrypt(row["notes_enc"]) if row["notes_enc"] else ""
            reencrypted.append(
                (
                    row["id"],
                    new_cipher.encrypt(password),
                    new_cipher.encrypt(notes) if notes else "",
                )
            )

        verifier = new_cipher.encrypt(crypto.VERIFIER_PLAINTEXT).encode("ascii")
        self._db.replace_key_material(new_salt, verifier, reencrypted)
        self._cipher = new_cipher

    # ------------------------------------------------------------------- CRUD
    def add_entry(
        self, service: str, username: str, password: str, notes: str = ""
    ) -> int:
        cipher = self._require_cipher()
        service, username = self._clean_fields(service, username, password)
        return self._db.add_entry(
            service,
            username,
            cipher.encrypt(password),
            cipher.encrypt(notes) if notes else "",
        )

    def list_entries(self, search: str = "") -> list:
        """Entries without passwords (fast, safe to show in a table)."""
        self._require_cipher()
        return [
            Entry(
                id=row["id"],
                service=row["service"],
                username=row["username"],
                password=None,
                notes="",
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in self._db.list_entries(search.strip())
        ]

    def get_entry(self, entry_id: int) -> Entry:
        """Fetch one entry with its password and notes decrypted."""
        cipher = self._require_cipher()
        row = self._db.get_entry(entry_id)
        if row is None:
            raise EntryNotFoundError(entry_id)
        return Entry(
            id=row["id"],
            service=row["service"],
            username=row["username"],
            password=cipher.decrypt(row["password_enc"]),
            notes=cipher.decrypt(row["notes_enc"]) if row["notes_enc"] else "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def update_entry(
        self,
        entry_id: int,
        service: str,
        username: str,
        password: str,
        notes: str = "",
    ) -> None:
        cipher = self._require_cipher()
        service, username = self._clean_fields(service, username, password)
        updated = self._db.update_entry(
            entry_id,
            service,
            username,
            cipher.encrypt(password),
            cipher.encrypt(notes) if notes else "",
        )
        if not updated:
            raise EntryNotFoundError(entry_id)

    def delete_entry(self, entry_id: int) -> None:
        self._require_cipher()
        if not self._db.delete_entry(entry_id):
            raise EntryNotFoundError(entry_id)

    def close(self) -> None:
        self.lock()
        self._db.close()

    # ---------------------------------------------------------------- helpers
    def _require_cipher(self) -> Cipher:
        if self._cipher is None:
            raise VaultLockedError("Unlock the vault first.")
        return self._cipher

    def _verified_cipher(self, master_password: str) -> Cipher:
        salt = self._db.get_meta("salt")
        verifier = self._db.get_meta("verifier")
        if salt is None or verifier is None:
            raise RuntimeError("No vault exists yet - create one first.")
        cipher = Cipher(crypto.derive_key(master_password, salt))
        try:
            ok = cipher.decrypt(verifier.decode("ascii")) == crypto.VERIFIER_PLAINTEXT
        except CryptoError:
            ok = False
        if not ok:
            raise InvalidMasterPasswordError("Incorrect master password.")
        return cipher

    @staticmethod
    def _validate_master_password(password: str) -> None:
        if len(password) < config.MIN_MASTER_LENGTH:
            raise WeakMasterPasswordError(
                f"Master password must be at least {config.MIN_MASTER_LENGTH} characters."
            )

    @staticmethod
    def _clean_fields(service: str, username: str, password: str) -> tuple:
        service, username = service.strip(), username.strip()
        if not service:
            raise ValidationError("Service / website name is required.")
        if not password:
            raise ValidationError("Password cannot be empty.")
        return service, username
