"""Windowed installed entry point, with a writable startup log."""
import sys
import traceback

from app_paths import STATE_DIR


def launch():
    log_dir = STATE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / "launcher.log").open("a", encoding="utf-8", buffering=1) as log:
        sys.stdout = sys.stderr = log
        try:
            from gui import main
            main()
        except Exception:
            traceback.print_exc()
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Unable to open experiment", f"See the startup log:\n{log_dir / 'launcher.log'}", parent=root)
            root.destroy()
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(launch())
