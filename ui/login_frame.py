"""First screen: create a master password (first run) or unlock the vault."""

import tkinter as tk
from tkinter import ttk

import config
from core.manager import (
    InvalidMasterPasswordError,
    PasswordManager,
    WeakMasterPasswordError,
)


class LoginFrame(ttk.Frame):
    def __init__(self, parent, manager: PasswordManager, on_success):
        super().__init__(parent)
        self.manager = manager
        self.on_success = on_success
        self.is_setup = not manager.is_initialized
        self._failed_attempts = 0

        card = ttk.Frame(self, style="Card.TFrame", padding=(44, 36))
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="SecureVault", style="Card.Title.TLabel").grid(
            row=0, column=0, pady=(0, 2)
        )
        subtitle = (
            "Create a master password to protect your vault"
            if self.is_setup
            else "Welcome back - enter your master password"
        )
        ttk.Label(card, text=subtitle, style="Card.Muted.TLabel").grid(
            row=1, column=0, pady=(0, 24)
        )

        ttk.Label(card, text="Master password", style="Card.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 4)
        )
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            card, textvariable=self.password_var, show="*", width=36
        )
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 14))

        self.confirm_var = tk.StringVar()
        if self.is_setup:
            ttk.Label(card, text="Confirm master password", style="Card.TLabel").grid(
                row=4, column=0, sticky="w", pady=(0, 4)
            )
            self.confirm_entry = ttk.Entry(
                card, textvariable=self.confirm_var, show="*", width=36
            )
            self.confirm_entry.grid(row=5, column=0, sticky="ew", pady=(0, 14))

        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            card, text="Show password", variable=self.show_var,
            command=self._toggle_show, style="Card.TCheckbutton",
        ).grid(row=6, column=0, sticky="w")

        if self.is_setup:
            hint = (
                f"Use at least {config.MIN_MASTER_LENGTH} characters. "
                "If you forget it, your data CANNOT be recovered."
            )
            ttk.Label(
                card, text=hint, style="Card.Warning.TLabel", wraplength=330
            ).grid(row=7, column=0, pady=(12, 0), sticky="w")

        self.message_var = tk.StringVar()
        ttk.Label(card, textvariable=self.message_var, style="Card.Error.TLabel").grid(
            row=8, column=0, pady=(10, 0)
        )

        self.submit_btn = ttk.Button(
            card,
            text="Create vault" if self.is_setup else "Unlock",
            style="Primary.TButton",
            command=self._submit,
        )
        self.submit_btn.grid(row=9, column=0, pady=(14, 0), sticky="ew")

        self.password_entry.bind("<Return>", lambda _e: self._submit())
        if self.is_setup:
            self.confirm_entry.bind("<Return>", lambda _e: self._submit())
        self.password_entry.focus_set()

    # ---------------------------------------------------------------- actions
    def _toggle_show(self):
        char = "" if self.show_var.get() else "*"
        self.password_entry.configure(show=char)
        if self.is_setup:
            self.confirm_entry.configure(show=char)

    def _submit(self):
        if str(self.submit_btn["state"]) == "disabled":
            return
        password = self.password_var.get()
        try:
            if self.is_setup:
                if password != self.confirm_var.get():
                    self.message_var.set("Passwords do not match.")
                    return
                self.manager.create_vault(password)
            else:
                self.manager.unlock(password)
        except WeakMasterPasswordError as exc:
            self.message_var.set(str(exc))
            return
        except InvalidMasterPasswordError:
            self._register_failure()
            return

        self.password_var.set("")
        self.confirm_var.set("")
        self.on_success()

    def _register_failure(self):
        self._failed_attempts += 1
        self.password_var.set("")
        if self._failed_attempts >= config.MAX_LOGIN_ATTEMPTS:
            self._failed_attempts = 0
            self.submit_btn.configure(state="disabled")
            self._countdown(config.LOGIN_COOLDOWN_SECONDS)
        else:
            left = config.MAX_LOGIN_ATTEMPTS - self._failed_attempts
            self.message_var.set(f"Incorrect master password. {left} attempt(s) left.")

    def _countdown(self, seconds: int):
        if not self.winfo_exists():
            return
        if seconds <= 0:
            self.submit_btn.configure(state="normal")
            self.message_var.set("")
            return
        self.message_var.set(f"Too many attempts. Try again in {seconds}s.")
        self.after(1000, lambda: self._countdown(seconds - 1))
