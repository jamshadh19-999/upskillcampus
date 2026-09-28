"""Main screen: search, list, add, edit, delete and copy saved passwords."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable

import config
from core.manager import EntryNotFoundError, PasswordManager
from ui.dialogs import ChangeMasterDialog, EntryDialog, GeneratorDialog
from ui.theme import ROW_ALT


def _format_time(iso_text: str) -> str:
    """Turn a stored UTC ISO timestamp into a friendly local time."""
    try:
        return datetime.fromisoformat(iso_text).astimezone().strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso_text


class VaultFrame(ttk.Frame):
    def __init__(
        self,
        parent,
        manager: PasswordManager,
        on_lock: Callable[[], None],
        copy_secret: Callable[[str], None],
    ):
        super().__init__(parent)
        self.manager = manager
        self.on_lock = on_lock
        self.copy_secret = copy_secret

        self._build_header()
        body = ttk.Frame(self, padding=(22, 18, 22, 10))
        body.pack(fill="both", expand=True)
        self._build_search(body)
        self._build_actions(body)
        self._build_table(body)
        self._build_status_bar(body)

        self.search_var.trace_add("write", lambda *_: self.refresh())
        self.refresh()
        self.search_entry.focus_set()

    # ------------------------------------------------------------------- UI
    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=(22, 14))
        header.pack(fill="x")
        ttk.Label(header, text="SecureVault", style="Header.TLabel").pack(side="left")
        ttk.Button(header, text="Lock", style="Header.TButton", command=self.on_lock).pack(
            side="right"
        )
        ttk.Button(
            header, text="Change master password", style="Header.TButton",
            command=self._change_master,
        ).pack(side="right", padx=8)

    def _build_search(self, body):
        row = ttk.Frame(body)
        row.pack(fill="x", pady=(0, 12))
        ttk.Label(row, text="Search", style="Muted.TLabel").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(row, textvariable=self.search_var, width=40)
        self.search_entry.pack(side="left", padx=(10, 0))

    def _build_actions(self, body):
        row = ttk.Frame(body)
        row.pack(fill="x", pady=(0, 12))
        ttk.Button(row, text="+ Add", style="Primary.TButton", command=self._add).pack(
            side="left"
        )
        ttk.Button(row, text="Edit", command=self._edit).pack(side="left", padx=8)
        ttk.Button(row, text="Delete", style="Danger.TButton", command=self._delete).pack(
            side="left"
        )
        ttk.Separator(row, orient="vertical").pack(side="left", fill="y", padx=14)
        ttk.Button(row, text="Copy password", command=self._copy_password).pack(side="left")
        ttk.Button(row, text="Copy username", command=self._copy_username).pack(
            side="left", padx=8
        )
        ttk.Separator(row, orient="vertical").pack(side="left", fill="y", padx=14)
        ttk.Button(row, text="Password generator", command=self._open_generator).pack(
            side="left"
        )

    def _build_table(self, body):
        holder = ttk.Frame(body)
        holder.pack(fill="both", expand=True)

        columns = ("service", "username", "updated")
        self.tree = ttk.Treeview(holder, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("service", text="Service / Website", anchor="w")
        self.tree.heading("username", text="Username / Email", anchor="w")
        self.tree.heading("updated", text="Last updated", anchor="center")
        self.tree.column("service", width=260, anchor="w")
        self.tree.column("username", width=280, anchor="w")
        self.tree.column("updated", width=150, anchor="center")
        self.tree.tag_configure("alt", background=ROW_ALT)

        scrollbar = ttk.Scrollbar(holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda _e: self._edit())
        self.tree.bind("<Return>", lambda _e: self._edit())
        self.tree.bind("<Delete>", lambda _e: self._delete())

        # Friendly message shown on top of the empty table.
        self.empty_label = ttk.Label(holder, style="Card.Muted.TLabel", justify="center")

    def _build_status_bar(self, body):
        self.status_var = tk.StringVar()
        ttk.Label(body, textvariable=self.status_var, style="Muted.TLabel").pack(
            fill="x", pady=(10, 0)
        )

    # ----------------------------------------------------------------- data
    def refresh(self):
        selected = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        query = self.search_var.get()
        entries = self.manager.list_entries(query)
        for index, entry in enumerate(entries):
            self.tree.insert(
                "", "end", iid=str(entry.id),
                values=(entry.service, entry.username, _format_time(entry.updated_at)),
                tags=("alt",) if index % 2 else (),
            )
        if selected and self.tree.exists(selected[0]):
            self.tree.selection_set(selected[0])

        total = len(entries)
        if total == 0:
            message = (
                "No matching entries found."
                if query.strip()
                else "No passwords saved yet.\nClick  + Add  to create your first entry."
            )
            self.empty_label.configure(text=message)
            self.empty_label.place(in_=self.tree, relx=0.5, rely=0.55, anchor="center")
        else:
            self.empty_label.place_forget()

        self.status_var.set(
            f"{total} saved account{'s' if total != 1 else ''}"
            f"   |   Auto-locks after {config.AUTO_LOCK_MINUTES} min of inactivity"
        )

    def _selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Select an entry", "Please select an entry first.", parent=self)
            return None
        return int(selection[0])

    # -------------------------------------------------------------- actions
    def _add(self):
        dialog = EntryDialog(self, self.manager)
        dialog.show()
        if dialog.saved:
            self.refresh()
            self.status_var.set("Entry added.")

    def _edit(self):
        entry_id = self._selected_id()
        if entry_id is None:
            return
        try:
            entry = self.manager.get_entry(entry_id)
        except EntryNotFoundError:
            self.refresh()
            return
        dialog = EntryDialog(self, self.manager, entry)
        dialog.show()
        if dialog.saved:
            self.refresh()
            self.status_var.set("Entry updated.")

    def _delete(self):
        entry_id = self._selected_id()
        if entry_id is None:
            return
        service = self.tree.set(str(entry_id), "service")
        if not messagebox.askyesno(
            "Delete entry", f"Permanently delete the entry for '{service}'?", parent=self
        ):
            return
        try:
            self.manager.delete_entry(entry_id)
        except EntryNotFoundError:
            pass
        self.refresh()
        self.status_var.set("Entry deleted.")

    def _copy_password(self):
        entry_id = self._selected_id()
        if entry_id is None:
            return
        entry = self.manager.get_entry(entry_id)
        self.copy_secret(entry.password)
        self.status_var.set(
            f"Password copied. Clipboard clears in {config.CLIPBOARD_CLEAR_SECONDS}s."
        )

    def _copy_username(self):
        entry_id = self._selected_id()
        if entry_id is None:
            return
        entry = self.manager.get_entry(entry_id)
        self.clipboard_clear()
        self.clipboard_append(entry.username)
        self.status_var.set("Username copied.")

    def _open_generator(self):
        GeneratorDialog(self, on_copy=self.copy_secret).show()

    def _change_master(self):
        dialog = ChangeMasterDialog(self, self.manager)
        dialog.show()
        if dialog.changed:
            self.status_var.set("Master password changed.")
