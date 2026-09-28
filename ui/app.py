"""Root window: switches between the login screen and the vault screen, and
handles auto-lock and clipboard clearing."""

import tkinter as tk
from tkinter import ttk

import config
from core.manager import PasswordManager
from ui import theme
from ui.login_frame import LoginFrame
from ui.vault_frame import VaultFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(config.APP_NAME)
        self.geometry("900x580")
        self.minsize(780, 460)
        theme.apply_theme(self)

        self.manager = PasswordManager()
        self._current_frame = None
        self._idle_job = None
        self._clipboard_job = None

        # Any keyboard / mouse activity resets the inactivity timer.
        for sequence in ("<Key>", "<Button>", "<Motion>"):
            self.bind_all(sequence, self._reset_idle_timer, add="+")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.show_login()

    # ------------------------------------------------------------- screens
    def _swap_frame(self, frame: ttk.Frame):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame
        frame.pack(fill="both", expand=True)

    def show_login(self):
        self._cancel_idle_timer()
        self._swap_frame(LoginFrame(self, self.manager, on_success=self.show_vault))

    def show_vault(self):
        self._swap_frame(
            VaultFrame(self, self.manager, on_lock=self.lock, copy_secret=self.copy_secret)
        )
        self._reset_idle_timer()

    def lock(self):
        """Lock the vault, close any open dialogs and go back to the login screen."""
        for child in self.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.destroy()
        self.manager.lock()
        self.show_login()

    # ---------------------------------------------------------- auto-lock
    def _reset_idle_timer(self, _event=None):
        if not self.manager.is_unlocked:
            return
        self._cancel_idle_timer()
        self._idle_job = self.after(config.AUTO_LOCK_MINUTES * 60 * 1000, self.lock)

    def _cancel_idle_timer(self):
        if self._idle_job is not None:
            self.after_cancel(self._idle_job)
            self._idle_job = None

    # ---------------------------------------------------------- clipboard
    def copy_secret(self, text: str):
        """Copy text to the clipboard and wipe it again after a short delay."""
        self.clipboard_clear()
        self.clipboard_append(text)
        if self._clipboard_job is not None:
            self.after_cancel(self._clipboard_job)
        self._clipboard_job = self.after(
            config.CLIPBOARD_CLEAR_SECONDS * 1000, lambda: self._clear_clipboard(text)
        )

    def _clear_clipboard(self, text: str):
        self._clipboard_job = None
        try:
            if self.clipboard_get() == text:  # don't wipe something the user copied later
                self.clipboard_clear()
        except tk.TclError:
            pass  # clipboard empty or not text

    # ------------------------------------------------------------- shutdown
    def _on_close(self):
        self.manager.close()
        self.destroy()
