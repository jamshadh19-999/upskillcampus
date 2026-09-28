"""Look & feel of the whole app: colours, fonts and ttk styles.

Change a colour here and it changes everywhere. To re-colour the app, edit the
palette below (e.g. swap PRIMARY for a green such as "#059669").
"""

from tkinter import ttk

# ------------------------------------------------------------------ palette
BG = "#f1f5f9"             # window background (soft grey-blue)
CARD = "#ffffff"           # cards, table, input fields
HEADER = "#1e1b4b"         # dark top bar
HEADER_BTN = "#312e81"     # buttons on the dark top bar

PRIMARY = "#4f46e5"        # main accent (indigo)
PRIMARY_HOVER = "#4338ca"
PRIMARY_PRESSED = "#3730a3"
PRIMARY_SOFT = "#e0e7ff"   # selected table row

DANGER = "#dc2626"
DANGER_HOVER = "#b91c1c"
DANGER_PRESSED = "#991b1b"

TEXT = "#0f172a"
MUTED = "#64748b"
BORDER = "#e2e8f0"
BORDER_STRONG = "#cbd5e1"
WARNING = "#b45309"
ROW_ALT = "#f8fafc"        # every second table row

# Password strength colours: Very weak ... Very strong
STRENGTH_COLORS = ["#dc2626", "#ea580c", "#ca8a04", "#16a34a", "#15803d"]

# -------------------------------------------------------------------- fonts
FONT_FAMILY = "Segoe UI"   # falls back automatically on macOS / Linux
FONT = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_HEADING = (FONT_FAMILY, 14, "bold")
FONT_TITLE = (FONT_FAMILY, 26, "bold")
FONT_MONO = ("Consolas", 13)


def apply_theme(root) -> None:
    """Configure every ttk style used by the app. Call once at start-up."""
    root.configure(background=BG)
    root.option_add("*Font", FONT)

    style = ttk.Style(root)
    style.theme_use("clam")  # 'clam' respects custom colours on every platform

    # ------------------------------------------------------------- frames
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("Header.TFrame", background=HEADER)

    # ------------------------------------------------------------- labels
    variants = {
        "": {"foreground": TEXT, "font": FONT},
        "Title.": {"foreground": PRIMARY, "font": FONT_TITLE},
        "Heading.": {"foreground": TEXT, "font": FONT_HEADING},
        "Muted.": {"foreground": MUTED, "font": FONT},
        "Error.": {"foreground": DANGER, "font": FONT},
        "Warning.": {"foreground": WARNING, "font": FONT},
    }
    for group, background in (("", BG), ("Card.", CARD)):
        for name, options in variants.items():
            style.configure(f"{group}{name}TLabel", background=background, **options)
    style.configure(
        "Header.TLabel", background=HEADER, foreground="#ffffff", font=FONT_HEADING
    )

    # ------------------------------------------------------------ buttons
    style.configure(
        "TButton",
        font=FONT, padding=(14, 7), relief="flat",
        background=CARD, foreground=TEXT,
        bordercolor=BORDER_STRONG, lightcolor=CARD, darkcolor=CARD,
        focuscolor=CARD, focusthickness=0,
    )
    style.map(
        "TButton",
        background=[("disabled", BG), ("pressed", BORDER), ("active", BG)],
        foreground=[("disabled", "#94a3b8")],
        bordercolor=[("active", MUTED)],
    )

    def coloured_button(name, colour, hover, pressed):
        disabled = "#cbd5e1"
        style.configure(
            name,
            font=FONT_BOLD, padding=(14, 7), relief="flat",
            background=colour, foreground="#ffffff",
            bordercolor=colour, lightcolor=colour, darkcolor=colour,
            focuscolor=colour, focusthickness=0,
        )
        states = [("disabled", disabled), ("pressed", pressed), ("active", hover)]
        style.map(
            name,
            background=states,
            bordercolor=states,
            lightcolor=states,
            darkcolor=states,
            foreground=[("disabled", "#f8fafc")],
        )

    coloured_button("Primary.TButton", PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED)
    coloured_button("Danger.TButton", DANGER, DANGER_HOVER, DANGER_PRESSED)
    coloured_button("Header.TButton", HEADER_BTN, PRIMARY_HOVER, PRIMARY_PRESSED)

    # ------------------------------------------------------- input fields
    style.configure(
        "TEntry",
        fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT, padding=6,
        bordercolor=BORDER_STRONG, lightcolor=BORDER_STRONG, darkcolor=BORDER_STRONG,
    )
    focus = [("focus", PRIMARY)]
    style.map("TEntry", bordercolor=focus, lightcolor=focus, darkcolor=focus)

    style.configure(
        "TSpinbox",
        fieldbackground=CARD, background=CARD, foreground=TEXT, padding=4,
        arrowcolor=TEXT, bordercolor=BORDER_STRONG,
        lightcolor=BORDER_STRONG, darkcolor=BORDER_STRONG,
    )
    style.map("TSpinbox", bordercolor=focus, lightcolor=focus, darkcolor=focus)

    # ------------------------------------------------------- check buttons
    for name, background in (("TCheckbutton", BG), ("Card.TCheckbutton", CARD)):
        style.configure(name, background=background, foreground=TEXT, font=FONT)
        style.map(name, background=[("active", background)])

    # -------------------------------------------------------------- table
    style.configure(
        "Treeview",
        font=FONT, rowheight=34,
        background=CARD, fieldbackground=CARD, foreground=TEXT,
        borderwidth=0, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
    )
    style.map(
        "Treeview",
        background=[("selected", PRIMARY_SOFT)],
        foreground=[("selected", TEXT)],
    )
    style.configure(
        "Treeview.Heading",
        font=FONT_BOLD, padding=(10, 9), relief="flat", borderwidth=0,
        background=HEADER, foreground="#ffffff",
    )
    style.map("Treeview.Heading", background=[("active", HEADER_BTN)])

    style.configure(
        "Vertical.TScrollbar",
        background=BORDER_STRONG, troughcolor=BG, bordercolor=BG,
        lightcolor=BORDER_STRONG, darkcolor=BORDER_STRONG, arrowcolor=MUTED,
        relief="flat",
    )
    style.map("Vertical.TScrollbar", background=[("active", MUTED)])

    style.configure("TSeparator", background=BORDER_STRONG)

    # -------------------------------------------------- strength meter bars
    for score, colour in enumerate(STRENGTH_COLORS):
        style.configure(
            f"Strength{score}.Horizontal.TProgressbar",
            troughcolor=BORDER, background=colour, bordercolor=BORDER,
            lightcolor=colour, darkcolor=colour, thickness=8,
        )
