import sqlite3
import tempfile
import unittest
from pathlib import Path

import config
from core.manager import (
    EntryNotFoundError,
    InvalidMasterPasswordError,
    PasswordManager,
    ValidationError,
    VaultLockedError,
    WeakMasterPasswordError,
)

MASTER = "correct-horse-battery"


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self._orig = config.KDF_ITERATIONS
        config.KDF_ITERATIONS = 1000
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "vault.db"
        self.pm = PasswordManager(self.db_path)
        self.pm.create_vault(MASTER)

    def tearDown(self):
        self.pm.close()
        self._tmp.cleanup()
        config.KDF_ITERATIONS = self._orig

    # ------------------------------------------------------------ vault setup
    def test_new_vault_state(self):
        self.assertTrue(self.pm.is_initialized)
        self.assertTrue(self.pm.is_unlocked)

    def test_cannot_create_twice(self):
        with self.assertRaises(RuntimeError):
            self.pm.create_vault(MASTER)

    def test_short_master_password_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = PasswordManager(Path(tmp) / "x.db")
            with self.assertRaises(WeakMasterPasswordError):
                other.create_vault("short")
            self.assertFalse(other.is_initialized)
            other.close()

    def test_lock_and_unlock(self):
        self.pm.lock()
        self.assertFalse(self.pm.is_unlocked)
        with self.assertRaises(VaultLockedError):
            self.pm.list_entries()
        with self.assertRaises(InvalidMasterPasswordError):
            self.pm.unlock("wrong-password!!")
        self.assertFalse(self.pm.is_unlocked)
        self.pm.unlock(MASTER)
        self.assertTrue(self.pm.is_unlocked)

    # ------------------------------------------------------------------- CRUD
    def test_add_and_get(self):
        entry_id = self.pm.add_entry("GitHub", "alice", "s3cret!", "2FA on phone")
        entry = self.pm.get_entry(entry_id)
        self.assertEqual(
            (entry.service, entry.username, entry.password, entry.notes),
            ("GitHub", "alice", "s3cret!", "2FA on phone"),
        )

    def test_passwords_are_encrypted_on_disk(self):
        self.pm.add_entry("Bank", "bob", "PlainTextPassword123", "secret note")
        raw = sqlite3.connect(self.db_path)
        blob = " ".join(str(v) for row in raw.execute("SELECT * FROM entries") for v in row)
        raw.close()
        self.assertNotIn("PlainTextPassword123", blob)
        self.assertNotIn("secret note", blob)
        self.assertNotIn(MASTER, blob)

    def test_list_hides_passwords_and_search_works(self):
        self.pm.add_entry("GitHub", "alice", "pw1")
        self.pm.add_entry("Gmail", "alice@example.com", "pw2")
        self.pm.add_entry("Netflix", "bob", "pw3")
        everything = self.pm.list_entries()
        self.assertEqual([e.service for e in everything], ["GitHub", "Gmail", "Netflix"])
        self.assertTrue(all(e.password is None for e in everything))
        self.assertEqual([e.service for e in self.pm.list_entries("gi")], ["GitHub"])
        self.assertEqual(len(self.pm.list_entries("ALICE")), 2)

    def test_search_treats_wildcards_literally(self):
        self.pm.add_entry("Site100%", "u", "pw")
        self.pm.add_entry("Other", "u", "pw")
        self.assertEqual([e.service for e in self.pm.list_entries("%")], ["Site100%"])
        self.assertEqual(self.pm.list_entries("_"), [])

    def test_update(self):
        entry_id = self.pm.add_entry("Old", "u", "old-pw")
        self.pm.update_entry(entry_id, "New", "u2", "new-pw", "note")
        entry = self.pm.get_entry(entry_id)
        self.assertEqual(
            (entry.service, entry.username, entry.password, entry.notes),
            ("New", "u2", "new-pw", "note"),
        )

    def test_delete(self):
        entry_id = self.pm.add_entry("Temp", "u", "pw")
        self.pm.delete_entry(entry_id)
        with self.assertRaises(EntryNotFoundError):
            self.pm.get_entry(entry_id)
        with self.assertRaises(EntryNotFoundError):
            self.pm.delete_entry(entry_id)

    def test_validation(self):
        with self.assertRaises(ValidationError):
            self.pm.add_entry("  ", "u", "pw")
        with self.assertRaises(ValidationError):
            self.pm.add_entry("Site", "u", "")

    def test_sql_injection_is_harmless(self):
        evil = "x'); DROP TABLE entries;--"
        entry_id = self.pm.add_entry(evil, evil, "pw")
        self.assertEqual(self.pm.get_entry(entry_id).service, evil)
        self.assertEqual(len(self.pm.list_entries(evil)), 1)

    # ---------------------------------------------------- persistence / rekey
    def test_data_survives_restart(self):
        self.pm.add_entry("Persist", "u", "pw-persist")
        self.pm.close()
        self.pm = PasswordManager(self.db_path)
        self.assertTrue(self.pm.is_initialized)
        self.assertFalse(self.pm.is_unlocked)
        self.pm.unlock(MASTER)
        entry = self.pm.get_entry(self.pm.list_entries()[0].id)
        self.assertEqual(entry.password, "pw-persist")

    def test_change_master_password(self):
        a = self.pm.add_entry("A", "u", "pw-a", "note-a")
        b = self.pm.add_entry("B", "u", "pw-b")
        new_master = "brand-new-master-pw"

        with self.assertRaises(InvalidMasterPasswordError):
            self.pm.change_master_password("not-the-old-one", new_master)
        with self.assertRaises(WeakMasterPasswordError):
            self.pm.change_master_password(MASTER, "short")

        self.pm.change_master_password(MASTER, new_master)
        self.assertEqual(self.pm.get_entry(a).password, "pw-a")

        self.pm.lock()
        with self.assertRaises(InvalidMasterPasswordError):
            self.pm.unlock(MASTER)  # old password no longer works
        self.pm.unlock(new_master)
        self.assertEqual(self.pm.get_entry(a).notes, "note-a")
        self.assertEqual(self.pm.get_entry(b).password, "pw-b")


if __name__ == "__main__":
    unittest.main()
