"""Entry point.  Run with:   python main.py"""

import sys


def main() -> int:
    try:
        import tkinter  # noqa: F401  (just checking it is installed)
    except ImportError:
        print(
            "Tkinter is not installed.\n"
            "  Windows/macOS: reinstall Python from python.org (tick 'tcl/tk').\n"
            "  Ubuntu/Debian: sudo apt install python3-tk",
            file=sys.stderr,
        )
        return 1

    try:
        import cryptography  # noqa: F401
    except ImportError:
        print(
            "The 'cryptography' package is missing.\n"
            "Run:  pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    from ui.app import App

    App().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
