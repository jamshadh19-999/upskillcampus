"""Central configuration for the Password Manager."""

from pathlib import Path

APP_NAME = "SecureVault - Password Manager"

# --- Storage -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "vault.db"

# --- Cryptography ------------------------------------------------------------
# Number of PBKDF2 rounds used to turn the master password into an encryption
# key. Higher = slower for attackers (and slightly slower for you).
KDF_ITERATIONS = 480_000
SALT_SIZE = 16  # bytes

# --- Master password rules ---------------------------------------------------
MIN_MASTER_LENGTH = 10

# --- Password generator defaults --------------------------------------------
DEFAULT_PASSWORD_LENGTH = 16
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64

# --- Security behaviour ------------------------------------------------------
CLIPBOARD_CLEAR_SECONDS = 20   # wipe the clipboard after copying a password
AUTO_LOCK_MINUTES = 5          # lock the vault after this much inactivity
MAX_LOGIN_ATTEMPTS = 5         # wrong master passwords before a cool-down
LOGIN_COOLDOWN_SECONDS = 30
