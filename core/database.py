"""SQLite storage layer.

This module only knows about *storing* data. It never sees the master password
or plaintext secrets - everything sensitive arrives here already encrypted.

Tables
------
meta     key/value pairs (the salt and the master-password verifier)
entries  one row per saved account
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    service       TEXT NOT NULL,
    username      TEXT NOT NULL,
    password_enc  TEXT NOT NULL,
    notes_enc     TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _escape_like(text: str) -> str:
    """Escape LIKE wildcards so user input is matched literally."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class Database:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    # ------------------------------------------------------------------ meta
    def get_meta(self, key: str) -> Optional[bytes]:
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return bytes(row["value"]) if row else None

    def replace_key_material(
        self,
        salt: bytes,
        verifier: bytes,
        reencrypted: Iterable[tuple] = (),
    ) -> None:
        """Atomically store a new salt + verifier and (optionally) re-encrypted
        secrets as (entry_id, password_enc, notes_enc) tuples.

        Everything happens in ONE transaction, so a crash half-way can never
        leave the vault with a new salt but old ciphertexts.
        """
        with self._conn:  # commits on success, rolls back on error
            self._conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('salt', ?)", (salt,)
            )
            self._conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('verifier', ?)",
                (verifier,),
            )
            for entry_id, password_enc, notes_enc in reencrypted:
                self._conn.execute(
                    "UPDATE entries SET password_enc = ?, notes_enc = ? WHERE id = ?",
                    (password_enc, notes_enc, entry_id),
                )

    # --------------------------------------------------------------- entries
    def add_entry(
        self, service: str, username: str, password_enc: str, notes_enc: str
    ) -> int:
        now = _now()
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO entries "
                "(service, username, password_enc, notes_enc, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (service, username, password_enc, notes_enc, now, now),
            )
        return cur.lastrowid

    def get_entry(self, entry_id: int) -> Optional[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()

    def list_entries(self, search: str = "") -> list:
        """Return entries WITHOUT secrets, optionally filtered by service/username."""
        query = (
            "SELECT id, service, username, created_at, updated_at FROM entries"
        )
        params: tuple = ()
        if search:
            like = f"%{_escape_like(search)}%"
            query += " WHERE service LIKE ? ESCAPE '\\' OR username LIKE ? ESCAPE '\\'"
            params = (like, like)
        query += " ORDER BY service COLLATE NOCASE, username COLLATE NOCASE"
        return self._conn.execute(query, params).fetchall()

    def all_secrets(self) -> list:
        return self._conn.execute(
            "SELECT id, password_enc, notes_enc FROM entries"
        ).fetchall()

    def update_entry(
        self,
        entry_id: int,
        service: str,
        username: str,
        password_enc: str,
        notes_enc: str,
    ) -> bool:
        with self._conn:
            cur = self._conn.execute(
                "UPDATE entries SET service = ?, username = ?, password_enc = ?, "
                "notes_enc = ?, updated_at = ? WHERE id = ?",
                (service, username, password_enc, notes_enc, _now(), entry_id),
            )
        return cur.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        with self._conn:
            cur = self._conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        return cur.rowcount > 0

    # ----------------------------------------------------------------- misc
    def close(self) -> None:
        self._conn.close()
