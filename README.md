# SecureVault - Python Password Manager

A desktop password manager built with Python. It stores account passwords in an
encrypted local database, generates strong passwords and lets you search, edit
and copy your saved credentials from a simple graphical interface.

## Features

- **Master password** protects everything (never stored anywhere)
- **Strong encryption**: passwords and notes are encrypted with Fernet (AES + HMAC)
  using a key derived from your master password with PBKDF2-SHA256 (480,000 rounds)
- **Password generator**: cryptographically secure (`secrets`), custom length,
  character types and an option to avoid look-alike characters
- **Strength meter** for any password you type or generate
- **Modern styled interface**: indigo theme, dark header bar, striped table,
  colour-coded strength meter (all colours live in `ui/theme.py`)
- **Full CRUD**: add, view/edit, delete and search entries
- **Copy to clipboard** with automatic clearing after 20 seconds
- **Auto-lock** after 5 minutes of inactivity, plus a manual Lock button
- **Brute-force slow-down**: 5 wrong master passwords = 30-second cool-down
- **Change master password**: re-encrypts every entry safely (all-or-nothing)
- **SQLite database** with parameterised queries (safe from SQL injection)
- **26 automated unit tests**

## Folder structure

```
password_manager/
|-- main.py                  # start the app
|-- config.py                # all settings in one place
|-- requirements.txt         # Python packages to install
|-- README.md
|-- .gitignore
|-- core/                    # logic (no UI code here)
|   |-- crypto.py            # key derivation + encrypt/decrypt
|   |-- database.py          # SQLite storage
|   |-- generator.py         # password generator + strength meter
|   `-- manager.py           # PasswordManager: ties everything together
|-- ui/                      # Tkinter interface
|   |-- theme.py             # colours, fonts and styles (edit this to re-colour the app)
|   |-- app.py               # main window, auto-lock, clipboard clearing
|   |-- login_frame.py       # create-vault / unlock screen
|   |-- vault_frame.py       # main table of saved passwords
|   `-- dialogs.py           # add/edit, generator, change-master dialogs
|-- tests/                   # unit tests
|   |-- test_crypto_and_generator.py
|   `-- test_manager.py
`-- data/                    # vault.db is created here on first run
```

## Setup

You need **Python 3.9 or newer** (Tkinter comes bundled with the Windows/macOS
installers from python.org; on Ubuntu/Debian run `sudo apt install python3-tk`).

```bash
# 1. open a terminal inside the password_manager folder

# 2. (recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS / Linux

# 3. install dependencies
pip install -r requirements.txt

# 4. run the app
python main.py
```

On first launch you'll be asked to create a master password. On later launches
you'll just unlock with it.

## Run the tests

```bash
python -m unittest discover -v
```

## How the security works

1. You create a master password. A random 16-byte **salt** is generated.
2. **PBKDF2-HMAC-SHA256** stretches `master password + salt` into a 32-byte key.
   This is deliberately slow, so guessing passwords offline is expensive.
3. Every password and note is encrypted with that key (**Fernet** = AES-128-CBC
   + HMAC-SHA256). Encryption is authenticated, so tampering is detected.
4. To check your master password at login, the app decrypts a small stored
   "verifier" value. If that works, the key is right. The master password
   itself and the key are **never written to disk**.
5. Locking the vault discards the key from memory.

## Known limitations (good to mention in your report)

- Service names and usernames are stored unencrypted so search works; only
  passwords and notes are encrypted.
- If you forget the master password there is **no recovery**. That is by design.
- Python cannot guarantee wiping secrets from RAM; a determined attacker with
  access to your running computer could still capture them.
- Single-user, local-only (no cloud sync).

## Ideas to extend the project

- Export / import an encrypted backup (JSON or CSV)
- Categories / tags and favourites
- Password-age reminders and duplicate/weak-password report
- Check passwords against breach lists (Have I Been Pwned k-anonymity API)
- Two-factor unlock, or a command-line version using `argparse`
- Package as a `.exe` with PyInstaller
