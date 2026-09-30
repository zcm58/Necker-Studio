"""Windowed installed entry point, with a writable startup log."""
import sys
import traceback

from app_paths import STATE_DIR


def launch():
    # Inno refuses installation while any installed GUI is still alive.
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    mutex = kernel.CreateMutexW(None, False, r"Local\NeckerExperimentRunning")
    if not mutex:
        raise ctypes.WinError(ctypes.get_last_error())
    # Windows closes this handle when the GUI process exits.
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
