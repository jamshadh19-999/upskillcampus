"""Pop-up windows used by the main vault screen."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

import config
from core.generator import check_strength, generate_password
from core.manager import (
    Entry,
    InvalidMasterPasswordError,
    PasswordManager,
    ValidationError,
    WeakMasterPasswordError,
)
from ui import theme


class BaseDialog(tk.Toplevel):
    """Modal, centred pop-up window."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        self.configure(background=theme.BG)
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.body = ttk.Frame(self, padding=(22, 18))
        self.body.pack(fill="both", expand=True)

    def show(self):
        self.update_idletasks()
        root = self.master.winfo_toplevel()
        x = root.winfo_x() + (root.winfo_width() - self.winfo_width()) // 2
        y = root.winfo_y() + (root.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        self.wait_visibility()
        self.grab_set()
        self.bind("<Escape>", lambda _e: self.destroy())
        self.wait_window(self)


class StrengthMeter(ttk.Frame):
    """A coloured bar plus a label such as 'Strong'."""

    def __init__(self, parent):
        super().__init__(parent)
        self.bar = ttk.Progressbar(
            self, length=190, maximum=100, mode="determinate",
            style="Strength0.Horizontal.TProgressbar",
        )
        self.bar.pack(side="left")
        self.text = tk.StringVar()
        self.label = ttk.Label(self, textvariable=self.text)
        self.label.pack(side="left", padx=(12, 0))

    def update_for(self, password: str):
        if not password:
            self.clear()
            return
        label, score = check_strength(password)
        self.bar.configure(
            style=f"Strength{score}.Horizontal.TProgressbar", value=(score + 1) * 20
        )
        self.text.set(label)
        self.label.configure(foreground=theme.STRENGTH_COLORS[score])

    def clear(self, message: str = ""):
        self.bar.configure(value=0)
        self.text.set(message)
        self.label.configure(foreground=theme.DANGER if message else theme.MUTED)


# =============================================================================
# Password generator
# =============================================================================
class GeneratorDialog(BaseDialog):
    def __init__(self, parent, on_use: Optional[Callable[[str], None]] = None,
                 on_copy: Optional[Callable[[str], None]] = None):
        super().__init__(parent, "Password Generator")
        self.on_use = on_use
        self.on_copy = on_copy

        b = self.body
        ttk.Label(b, text="Password generator", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        self.result_var = tk.StringVar()
        ttk.Entry(b, textvariable=self.result_var, width=34,
                  font=theme.FONT_MONO).grid(row=1, column=0, columnspan=3, sticky="ew")

        self.meter = StrengthMeter(b)
        self.meter.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 16))

        ttk.Label(b, text="Length").grid(row=3, column=0, sticky="w", pady=(0, 8))
        self.length_var = tk.IntVar(value=config.DEFAULT_PASSWORD_LENGTH)
        ttk.Spinbox(
            b, from_=config.MIN_PASSWORD_LENGTH, to=config.MAX_PASSWORD_LENGTH,
            textvariable=self.length_var, width=6, command=self._generate,
        ).grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(0, 8))

        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)
        options = [
            ("Uppercase letters (A-Z)", self.upper_var),
            ("Lowercase letters (a-z)", self.lower_var),
            ("Digits (0-9)", self.digits_var),
            ("Symbols (!@#$...)", self.symbols_var),
            ("Avoid look-alike characters (I, l, 1, O, 0)", self.ambiguous_var),
        ]
        for i, (text, var) in enumerate(options):
            ttk.Checkbutton(b, text=text, variable=var, command=self._generate).grid(
                row=4 + i, column=0, columnspan=3, sticky="w", pady=2
            )

        buttons = ttk.Frame(b)
        buttons.grid(row=9, column=0, columnspan=3, pady=(18, 0), sticky="e")
        ttk.Button(buttons, text="Regenerate", command=self._generate).pack(side="left")
        ttk.Button(
            buttons, text="Copy",
            style="TButton" if self.on_use else "Primary.TButton",
            command=self._copy,
        ).pack(side="left", padx=8)
        ttk.Button(buttons, text="Close", command=self.destroy).pack(side="left")
        if self.on_use:
            ttk.Button(
                buttons, text="Use this password", style="Primary.TButton",
                command=self._use,
            ).pack(side="left", padx=(8, 0))

        self._generate()

    def _generate(self):
        try:
            length = int(self.length_var.get())
            password = generate_password(
                length=length,
                use_upper=self.upper_var.get(),
                use_lower=self.lower_var.get(),
                use_digits=self.digits_var.get(),
                use_symbols=self.symbols_var.get(),
                exclude_ambiguous=self.ambiguous_var.get(),
            )
        except (ValueError, tk.TclError) as exc:
            self.result_var.set("")
            self.meter.clear(str(exc))
            return
        self.result_var.set(password)
        self.meter.update_for(password)

    def _copy(self):
        password = self.result_var.get()
        if not password:
            return
        if self.on_copy:
            self.on_copy(password)
        else:
            self.clipboard_clear()
            self.clipboard_append(password)

    def _use(self):
        password = self.result_var.get()
        if password and self.on_use:
            self.on_use(password)
            self.destroy()


# =============================================================================
# Add / edit an entry
# =============================================================================
class EntryDialog(BaseDialog):
    """Add a new entry, or edit an existing one when `entry` is given."""

    def __init__(self, parent, manager: PasswordManager, entry: Optional[Entry] = None):
        super().__init__(parent, "Edit entry" if entry else "Add new entry")
        self.manager = manager
        self.entry = entry
        self.saved = False

        b = self.body
        ttk.Label(
            b, text="Edit entry" if entry else "Add new entry", style="Heading.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))

        self.service_var = tk.StringVar(value=entry.service if entry else "")
        self.username_var = tk.StringVar(value=entry.username if entry else "")
        self.password_var = tk.StringVar(value=entry.password if entry else "")

        ttk.Label(b, text="Service / Website *").grid(row=1, column=0, sticky="w", pady=6)
        self.service_entry = ttk.Entry(b, textvariable=self.service_var, width=38)
        self.service_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(12, 0))

        ttk.Label(b, text="Username / Email").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(b, textvariable=self.username_var, width=38).grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=(12, 0)
        )

        ttk.Label(b, text="Password *").grid(row=3, column=0, sticky="w", pady=6)
        self.password_entry = ttk.Entry(b, textvariable=self.password_var, show="*", width=38)
        self.password_entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=(12, 0))

        controls = ttk.Frame(b)
        controls.grid(row=4, column=1, columnspan=2, sticky="ew", padx=(12, 0), pady=(4, 0))
        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Show password", variable=self.show_var,
                        command=self._toggle_show).pack(side="left")
        ttk.Button(controls, text="Generate...", command=self._open_generator).pack(
            side="right"
        )

        self.meter = StrengthMeter(b)
        self.meter.grid(row=5, column=1, columnspan=2, sticky="w", padx=(12, 0), pady=(10, 0))
        self.password_var.trace_add("write", lambda *_: self.meter.update_for(self.password_var.get()))
        self.meter.update_for(self.password_var.get())

        ttk.Label(b, text="Notes").grid(row=6, column=0, sticky="nw", pady=(14, 6))
        self.notes_text = tk.Text(
            b, width=38, height=5, wrap="word", font=theme.FONT,
            relief="flat", bg=theme.CARD, fg=theme.TEXT, insertbackground=theme.TEXT,
            highlightthickness=1, highlightbackground=theme.BORDER_STRONG,
            highlightcolor=theme.PRIMARY, padx=8, pady=6,
        )
        self.notes_text.grid(row=6, column=1, columnspan=2, sticky="ew", padx=(12, 0), pady=(14, 6))
        if entry:
            self.notes_text.insert("1.0", entry.notes)

        self.error_var = tk.StringVar()
        ttk.Label(b, textvariable=self.error_var, style="Error.TLabel").grid(
            row=7, column=0, columnspan=3, sticky="w"
        )

        buttons = ttk.Frame(b)
        buttons.grid(row=8, column=0, columnspan=3, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left")
        ttk.Button(buttons, text="Save", style="Primary.TButton", command=self._save).pack(
            side="left", padx=(8, 0)
        )

        self.service_entry.focus_set()

    def _toggle_show(self):
        self.password_entry.configure(show="" if self.show_var.get() else "*")

    def _open_generator(self):
        GeneratorDialog(self, on_use=self._use_generated).show()

    def _use_generated(self, password: str):
        self.password_var.set(password)
        self.show_var.set(True)
        self._toggle_show()

    def _save(self):
        notes = self.notes_text.get("1.0", "end-1c").strip()
        try:
            if self.entry:
                self.manager.update_entry(
                    self.entry.id, self.service_var.get(), self.username_var.get(),
                    self.password_var.get(), notes,
                )
            else:
                self.manager.add_entry(
                    self.service_var.get(), self.username_var.get(),
                    self.password_var.get(), notes,
                )
        except ValidationError as exc:
            self.error_var.set(str(exc))
            return
        self.saved = True
        self.destroy()


# =============================================================================
# Change master password
# =============================================================================
class ChangeMasterDialog(BaseDialog):
    def __init__(self, parent, manager: PasswordManager):
        super().__init__(parent, "Change master password")
        self.manager = manager
        self.changed = False

        b = self.body
        ttk.Label(b, text="Change master password", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        self.old_var = tk.StringVar()
        self.new_var = tk.StringVar()
        self.confirm_var = tk.StringVar()
        fields = [
            ("Current master password", self.old_var),
            ("New master password", self.new_var),
            ("Confirm new password", self.confirm_var),
        ]
        self.entries = []
        for i, (label, var) in enumerate(fields):
            ttk.Label(b, text=label).grid(row=1 + i, column=0, sticky="w", pady=6)
            entry = ttk.Entry(b, textvariable=var, show="*", width=32)
            entry.grid(row=1 + i, column=1, padx=(14, 0))
            self.entries.append(entry)

        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(b, text="Show passwords", variable=self.show_var,
                        command=self._toggle_show).grid(row=4, column=1, sticky="w",
                                                        padx=(14, 0), pady=4)

        ttk.Label(
            b, text=f"Use at least {config.MIN_MASTER_LENGTH} characters.",
            style="Muted.TLabel",
        ).grid(row=5, column=0, columnspan=2, sticky="w")

        self.error_var = tk.StringVar()
        ttk.Label(b, textvariable=self.error_var, style="Error.TLabel").grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )

        buttons = ttk.Frame(b)
        buttons.grid(row=7, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left")
        ttk.Button(buttons, text="Change", style="Primary.TButton", command=self._change).pack(
            side="left", padx=(8, 0)
        )
        self.entries[0].focus_set()

    def _toggle_show(self):
        char = "" if self.show_var.get() else "*"
        for entry in self.entries:
            entry.configure(show=char)

    def _change(self):
        if self.new_var.get() != self.confirm_var.get():
            self.error_var.set("New passwords do not match.")
            return
        try:
            self.manager.change_master_password(self.old_var.get(), self.new_var.get())
        except InvalidMasterPasswordError:
            self.error_var.set("Current master password is incorrect.")
            return
        except WeakMasterPasswordError as exc:
            self.error_var.set(str(exc))
            return
        self.changed = True
        messagebox.showinfo("Done", "Master password changed.", parent=self)
        self.destroy()
