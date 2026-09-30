"""Tk-owned update lifecycle; workers never access widgets or experiment data."""
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import updates
from window_layout import fit_window


class UpdateSettings(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=16)
        self.columnconfigure(0, weight=1)
        self.automatic = tk.BooleanVar(self, updates.load_preferences()["automatic"])
        ttk.Checkbutton(self, text="Check for updates at startup", variable=self.automatic).grid(row=0, column=0, sticky="w", pady=8)

    def save(self):
        updates.save_preferences(self.automatic.get())


class UpdateController:
    def __init__(self, app):
        self.app = app
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.thread = None
        self.dialog = None
        self.release = None
        self.path = None
        self.operation = ""
        self.installing = False
        self.shutting_down = False
        self.automatic = False
        self.status = None
        self.poll_id = None
        self.startup_id = None

    @property
    def working(self):
        return self.thread is not None

    def schedule(self):
        if (updates.APP_DIR / "release.json").is_file() and updates.load_preferences()["automatic"]:
            self.startup_id = self.app.after(3000, self.check_automatic)

    def check_automatic(self):
        self.startup_id = None
        if self.app.busy or self.shutting_down or self.working:
            return
        self.automatic = True
        self._job("check", self._check)

    def _check(self, cancel, notify):
        updates.cleanup_cache()
        return updates.check_for_updates(cancel=cancel)

    def open(self):
        if self.app.busy or self.shutting_down:
            return
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.lift()
            return
        self.automatic = False
        self._make_dialog()
        if not self.working:
            self._job("check", self._check)

    def _make_dialog(self):
        from gui import FlowButtons, PAGE
        self.dialog = dialog = tk.Toplevel(self.app)
        dialog.title("Updates")
        dialog.configure(background=PAGE)
        dialog.transient(self.app)
        fit_window(dialog, 620, 360)
        frame = ttk.Frame(dialog, padding=24)
        frame.pack(fill="both", expand=True)
        self.status = tk.StringVar(dialog, "Checking for updates…")
        label = ttk.Label(frame, textvariable=self.status, wraplength=530)
        label.pack(fill="x", pady=(0, 18))
        frame.bind("<Configure>", lambda event: label.configure(wraplength=max(80, event.width - 48)))
        self.progress = ttk.Progressbar(frame, maximum=100)
        self.progress.pack(fill="x", pady=8)
        self.force_full = tk.BooleanVar(dialog, False)
        self.full_option = ttk.Checkbutton(frame, text="Use full installer", variable=self.force_full, command=self._select, state="disabled")
        self.full_option.pack(anchor="w", pady=10)
        footer = self.footer = FlowButtons(dialog, padding=(18, 8, 18, 18))
        footer.pack(side="bottom", fill="x")
        self.action = footer.add("Download update", self.download, style="Primary.TButton", state="disabled")
        footer.add("Close", self.close_dialog)
        dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)
        dialog.bind("<Escape>", lambda event: self.close_dialog())
        dialog.grab_set()

    def _job(self, operation, function):
        if self.working:
            return
        self.operation = operation
        self.cancel = threading.Event()
        cancel = self.cancel
        def run():
            try:
                self.events.put(("done", function(cancel, lambda n, total: self.events.put(("progress", (n, total))))))
            except Exception as error:
                self.events.put(("error", error))
        self.thread = threading.Thread(target=run, name="necker-update", daemon=True)
        self.thread.start()
        self.poll_id = self.app.after(100, self._poll)

    def _poll(self):
        self.poll_id = None
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "progress":
                    if self.dialog is not None:
                        self.progress["value"] = value[0] * 100 / max(1, value[1])
                    continue
                self.thread.join(timeout=0)
                self.thread = None
                if self.shutting_down:
                    if self.operation == "install" and kind == "done":
                        self.installing = True
                    self.app.destroy()
                    return
                if kind == "error":
                    if self.dialog is not None and not isinstance(value, updates.Cancelled):
                        self.status.set(str(value))
                        self.action.configure(text="Retry", command=self.retry, state="normal")
                    elif self.dialog is not None:
                        self.status.set("Update cancelled.")
                    return
                self._done(value)
                return
        except queue.Empty:
            if self.working:
                self.poll_id = self.app.after(100, self._poll)

    def _done(self, value):
        if self.operation == "check":
            self.release = value
            if self.dialog is None and value is not None and not self.app.busy and not self.cancel.is_set():
                self.automatic = False
                self._make_dialog()
            if self.dialog is not None:
                self._select()
        elif self.operation == "download" and self.dialog is not None:
            self.path = value
            self.progress["value"] = 100
            self.status.set("Download verified. Ready to install.")
            self.action.configure(text="Install update", command=self.install, state="normal")
        elif self.operation == "install":
            self.installing = True
            self.app.destroy()

    def selected(self):
        if self.release is None:
            return None
        return self.release.full if self.force_full.get() else self.release.asset

    def _select(self):
        self.path = None
        if self.release is None:
            self.status.set("You're up to date.")
            self.action.configure(state="disabled")
            self.full_option.configure(state="disabled")
            return
        asset = self.selected()
        self.full_option.configure(state="normal" if self.release.asset and self.release.asset.kind == "patch" else "disabled")
        self.action.configure(text="Download update", command=self.download, state="normal" if asset else "disabled")
        if asset:
            self.status.set(f"Version {self.release.version} available — {asset.kind} installer ({asset.size / 1048576:.1f} MiB).")
        else:
            self.status.set(f"Version {self.release.version} available. {self.release.reason}")

    def retry(self):
        if self.working:
            return
        self.action.configure(state="disabled")
        self.status.set("Checking for updates…")
        self._job("check", self._check)

    def download(self):
        if self.working or self.app.busy:
            return
        asset = self.selected()
        if asset is None:
            return
        self.downloaded_asset = asset
        self.action.configure(state="disabled")
        self.full_option.configure(state="disabled")
        self.status.set("Downloading update…")
        self._job("download", lambda cancel, notify: updates.download(asset, cancel=cancel, progress=notify))

    def install(self):
        if self.working or self.app.busy or self.path is None:
            return
        if not messagebox.askyesno("Install update?", "Close the experiment application and install this update?", parent=self.dialog):
            return
        self.action.configure(state="disabled")
        self.status.set("Preparing installation…")
        self._job("install", lambda cancel, notify: updates.begin_install(self.downloaded_asset, self.path,
                   cancel=cancel))

    def close_dialog(self):
        self.cancel.set()
        if self.dialog is not None:
            self.dialog.destroy()
            self.dialog = None

    def pause_for_session(self):
        if self.startup_id is not None:
            self.app.after_cancel(self.startup_id)
            self.startup_id = None
        if self.working:
            self.cancel.set()

    def close_app(self):
        if not self.working:
            return False
        self.shutting_down = True
        self.cancel.set()
        self.app.status.set("Closing update check…")
        return True
