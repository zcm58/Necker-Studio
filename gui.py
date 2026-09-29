"""Small, dependency-free authoring shell for the PsychoPy experiment."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

if __package__:
    from . import runtime
    from .settings import (
        APP_DIR, CONDITION_CHOICES, CONDITION_COLUMNS, CONDITION_HELP,
        FIELD_SPECS, SETTINGS_PATH, default_settings, load_settings,
        save_settings, session_counts, validate_settings,
    )
else:
    import runtime
    from settings import (
        APP_DIR, CONDITION_CHOICES, CONDITION_COLUMNS, CONDITION_HELP,
        FIELD_SPECS, SETTINGS_PATH, default_settings, load_settings,
        save_settings, session_counts, validate_settings,
    )


PAGE = "#f4f7fb"
SURFACE = "#ffffff"
INK = "#1f2f44"
MUTED = "#53677d"
BORDER = "#d7dfea"
ACCENT = "#087e83"


def _apply_theme(root: tk.Tk) -> None:
    root.configure(background=PAGE)
    root.option_add("*Font", "{Segoe UI} 10")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 10), foreground=INK)
    style.configure("TFrame", background=PAGE)
    style.configure("TLabel", background=PAGE)
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("Title.TLabel", font=("Segoe UI", 25, "bold"))
    style.configure("Card.TFrame", background=SURFACE)
    style.configure("Card.TLabel", background=SURFACE)
    style.configure("CardMuted.TLabel", background=SURFACE, foreground=MUTED)
    style.configure("Heading.TLabel", background=SURFACE, font=("Segoe UI", 13, "bold"))
    style.configure("Metric.TLabel", background=SURFACE, foreground=ACCENT,
                    font=("Segoe UI", 25, "bold"))
    style.configure("TButton", padding=(12, 8), background="#eef3f9", borderwidth=1)
    style.map("TButton", background=[("active", "#e1eaf3")])
    style.configure("Primary.TButton", background=ACCENT, foreground="white",
                    font=("Segoe UI", 11, "bold"), borderwidth=0, padding=(20, 11))
    style.map("Primary.TButton", background=[("disabled", "#c4d4d9"), ("active", "#05666b")],
              foreground=[("disabled", "#53677d")])
    style.configure("TEntry", padding=7, fieldbackground=SURFACE)
    style.configure("TCombobox", padding=6, fieldbackground=SURFACE)
    style.configure("TCheckbutton", background=PAGE, padding=(0, 4))
    style.configure("TNotebook", background=PAGE, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(12, 8))
    style.map("TNotebook.Tab", background=[("selected", SURFACE)])
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, rowheight=29)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=6)
    style.map("Treeview", background=[("selected", "#d8eeee")],
              foreground=[("selected", INK)])


def _fit_window(window: tk.Toplevel | tk.Tk, width: int, height: int) -> None:
    """Keep the initial window inside the available screen, including small laptops."""
    width = min(width, max(520, window.winfo_screenwidth() - 80))
    height = min(height, max(380, window.winfo_screenheight() - 100))
    window.geometry(f"{width}x{height}")
    window.minsize(min(680, width), min(470, height))


def _open_path(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def _display(value: object) -> str:
    return "" if value is None else str(value)


class ScrollFrame(ttk.Frame):
    """Vertical scrolling without placing the dialog's action buttons off screen."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.canvas = tk.Canvas(self, background=PAGE, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.content = ttk.Frame(self.canvas, padding=(4, 4, 10, 12))
        self._window = self.canvas.create_window(0, 0, anchor="nw", window=self.content)
        self.content.bind("<Configure>", self._resize_content)
        self.canvas.bind("<Configure>", self._resize_canvas)
        self.winfo_toplevel().bind("<MouseWheel>", self._wheel, add="+")

    def _resize_content(self, _event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_canvas(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self._window, width=event.width)

    def _wheel(self, event: tk.Event) -> str | None:
        if not self.winfo_exists() or not str(event.widget).startswith(str(self)):
            return None
        if self.canvas.yview() == (0.0, 1.0):
            return None
        step = max(1, abs(event.delta) // 120)
        self.canvas.yview_scroll(-step if event.delta > 0 else step, "units")
        return "break"


class ConditionEditor(ttk.Frame):
    """A staged condition-table editor; no workbook changes are needed."""

    def __init__(self, parent: tk.Misc, filename: str, rows: list[dict]) -> None:
        super().__init__(parent, padding=12)
        self.filename = filename
        self.columns = list(CONDITION_COLUMNS[filename])
        self.rows = copy.deepcopy(rows)
        intro_label = ttk.Label(self, text=CONDITION_HELP[filename] + " Double-click a row to edit its values.",
                                style="Muted.TLabel", wraplength=680)
        intro_label.pack(anchor="w", pady=(0, 9))
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, columns=self.columns, show="headings", selectmode="browse")
        for column in self.columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=145 if column in {"image", "Sound"} else 95, minwidth=75)
        self.table.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.table.bind("<Double-1>", lambda _event: self.edit_row())
        self.table.bind("<Return>", lambda _event: self.edit_row())
        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Edit row…", command=self.edit_row).pack(side="left")
        if filename != "SoundEx.xlsx":
            ttk.Button(actions, text="Add", command=self.add_row).pack(side="left", padx=(7, 0))
            ttk.Button(actions, text="Duplicate", command=self.duplicate_row).pack(side="left", padx=(7, 0))
            ttk.Button(actions, text="Remove", command=self.remove_row).pack(side="left", padx=(7, 0))
        ttk.Button(actions, text="↑", width=3, command=lambda: self.move_row(-1)).pack(side="right", padx=(7, 0))
        ttk.Button(actions, text="↓", width=3, command=lambda: self.move_row(1)).pack(side="right")
        help_text = "Image and sound paths are relative to the assets folder, or may be absolute paths."
        if filename == "SoundEx.xlsx":
            help_text += " Four demonstration rows are required; the last row is the Go example."
        elif "ISI" in self.columns:
            help_text += " ISI is retained for compatibility and is unused by this protocol."
        help_label = ttk.Label(self, text=help_text, style="Muted.TLabel", wraplength=650)
        help_label.pack(anchor="w", pady=(10, 0))
        self.bind("<Configure>", lambda event: (
            intro_label.configure(wraplength=max(240, event.width - 30)),
            help_label.configure(wraplength=max(240, event.width - 30)),
        ))
        self.refresh()

    def refresh(self, select: int | None = None) -> None:
        self.table.delete(*self.table.get_children())
        for index, row in enumerate(self.rows):
            self.table.insert("", "end", iid=str(index), values=[_display(row.get(c)) for c in self.columns])
        if self.rows:
            index = min(max(select or 0, 0), len(self.rows) - 1)
            self.table.selection_set(str(index))
            self.table.see(str(index))

    def selected(self) -> int | None:
        selection = self.table.selection()
        return int(selection[0]) if selection else None

    def edit_row(self, *, new: bool = False) -> None:
        index = self.selected()
        if index is None and not new:
            return
        source = ({column: "" for column in self.columns} if new else self.rows[index])
        dialog = tk.Toplevel(self)
        dialog.title("Add condition" if new else f"Edit condition {index + 1}")
        dialog.configure(background=PAGE)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(True, True)
        _fit_window(dialog, 650, 530)
        scroll = ScrollFrame(dialog)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)
        scroll.content.columnconfigure(1, weight=1)
        variables = {}
        for row_index, column in enumerate(self.columns):
            ttk.Label(scroll.content, text=column).grid(row=row_index, column=0, sticky="w", padx=(0, 12), pady=7)
            variable = tk.StringVar(dialog, value=_display(source.get(column)))
            variables[column] = variable
            if column in CONDITION_CHOICES:
                entry = ttk.Combobox(scroll.content, textvariable=variable,
                                     values=CONDITION_CHOICES[column], state="readonly")
            else:
                entry = ttk.Entry(scroll.content, textvariable=variable)
            entry.grid(row=row_index, column=1, sticky="ew", pady=7)
            if column in {"image", "Sound", "choice"}:
                ttk.Button(scroll.content, text="Browse…", command=lambda v=variable: self._browse_asset(v, dialog)).grid(
                    row=row_index, column=2, padx=(7, 0))
        ttk.Label(scroll.content, text="delay: seconds. choice: choice-screen image. correct: Left or Right.\n"
                  "GoNoGo: space or None. ISI is unused; blank preserves the original value.",
                  style="Muted.TLabel", wraplength=500).grid(row=len(self.columns), column=0,
                                                             columnspan=3, sticky="w", pady=12)

        def apply() -> None:
            value = {column: variable.get().strip() for column, variable in variables.items()}
            try:
                for column in ("delay", "ISI"):
                    if column in value:
                        value[column] = None if column == "ISI" and not value[column] else float(value[column])
            except ValueError:
                messagebox.showerror("Check the condition", "delay and ISI must be numbers in seconds; ISI may be blank.", parent=dialog)
                return
            if new:
                self.rows.append(value)
                self.refresh(len(self.rows) - 1)
            else:
                self.rows[index] = value
                self.refresh(index)
            close()

        def close() -> None:
            dialog.grab_release()
            dialog.destroy()
            self.winfo_toplevel().grab_set()

        footer = ttk.Frame(dialog, padding=(16, 8, 16, 16))
        footer.pack(fill="x")
        ttk.Button(footer, text="Apply row", style="Primary.TButton", command=apply).pack(side="right")
        ttk.Button(footer, text="Cancel", command=close).pack(side="right", padx=(0, 8))
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.bind("<Escape>", lambda _event: close())

    def _browse_asset(self, variable: tk.StringVar, parent: tk.Toplevel) -> None:
        filename = filedialog.askopenfilename(parent=parent, title="Choose a stimulus file", initialdir=APP_DIR / "assets")
        if filename:
            path = Path(filename)
            try:
                value = path.relative_to(APP_DIR / "assets").as_posix()
            except ValueError:
                value = str(path)
            variable.set(value)

    def add_row(self) -> None:
        self.edit_row(new=True)

    def duplicate_row(self) -> None:
        index = self.selected()
        if index is not None:
            self.rows.insert(index + 1, copy.deepcopy(self.rows[index]))
            self.refresh(index + 1)

    def remove_row(self) -> None:
        index = self.selected()
        if index is None:
            return
        if len(self.rows) == 1:
            messagebox.showinfo("Keep one condition", "At least one condition row is required.", parent=self)
            return
        self.rows.pop(index)
        self.refresh(index)

    def move_row(self, step: int) -> None:
        index = self.selected()
        if index is not None and 0 <= index + step < len(self.rows):
            self.rows[index], self.rows[index + step] = self.rows[index + step], self.rows[index]
            self.refresh(index + step)


class SettingsDialog(tk.Toplevel):
    """All edits are staged until a validated, atomic save succeeds."""

    def __init__(self, parent: "NeckerApp") -> None:
        super().__init__(parent)
        self.app = parent
        self.draft = copy.deepcopy(parent.config)
        self.variables: dict[str, tk.Variable] = {}
        self.editors: dict[str, ConditionEditor] = {}
        self.title("Necker Studio — Settings")
        self.configure(background=PAGE)
        self.transient(parent)
        _fit_window(self, 960, 710)
        header = ttk.Frame(self, padding=(20, 16, 20, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Experiment settings", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(header, text="Saved settings apply to the next session.", style="Muted.TLabel").pack(anchor="w", pady=(4, 0))
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=18)
        groups: dict[str, ScrollFrame] = {}
        for spec in FIELD_SPECS:
            group = spec["group"]
            if group not in groups:
                groups[group] = ScrollFrame(self.notebook)
                self.notebook.add(groups[group], text=group)
            self._field(groups[group].content, spec)
        conditions = ttk.Notebook(self.notebook)
        self.notebook.add(conditions, text="Conditions")
        for filename in CONDITION_COLUMNS:
            editor = ConditionEditor(conditions, filename, self.draft["conditions"][filename])
            self.editors[filename] = editor
            conditions.add(editor, text=filename.removesuffix(".xlsx"))
        footer = ttk.Frame(self, padding=(18, 12, 18, 16))
        footer.pack(fill="x")
        ttk.Button(footer, text="Restore defaults", command=self.restore_defaults).pack(side="left")
        ttk.Button(footer, text="Save settings", style="Primary.TButton", command=self.save).pack(side="right")
        ttk.Button(footer, text="Cancel", command=self.destroy).pack(side="right", padx=(0, 8))
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    def _field(self, parent: ttk.Frame, spec: dict) -> None:
        frame = ttk.Frame(parent, padding=(12, 8))
        frame.pack(fill="x")
        frame.columnconfigure(1, weight=1)
        key, kind = spec["key"], spec["kind"]
        variable = (tk.BooleanVar(self, value=self.draft[key]) if kind == "bool"
                    else tk.StringVar(self, value=_display(self.draft[key])))
        self.variables[key] = variable
        if kind == "bool":
            ttk.Checkbutton(frame, text=spec["label"], variable=variable).grid(row=0, column=0, columnspan=3, sticky="w")
        else:
            ttk.Label(frame, text=spec["label"], width=29, wraplength=210).grid(row=0, column=0, sticky="w", padx=(0, 14))
            if spec.get("choices"):
                control = ttk.Combobox(frame, textvariable=variable, values=spec["choices"], state="readonly")
            else:
                control = ttk.Entry(frame, textvariable=variable)
            control.grid(row=0, column=1, sticky="ew")
            if kind in {"path", "directory", "file"} or key in {"psychopy_python", "output_dir"}:
                ttk.Button(frame, text="Browse…", command=lambda k=key, v=variable, s=spec: self._browse(k, v, s)).grid(
                    row=0, column=2, padx=(8, 0))
        if spec.get("help"):
            label = ttk.Label(frame, text=spec["help"], style="Muted.TLabel", wraplength=720)
            label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 0))
            frame.bind("<Configure>", lambda event, item=label: item.configure(wraplength=max(240, event.width - 24)))

    def _browse(self, key: str, variable: tk.Variable, spec: dict) -> None:
        if key == "output_dir" or spec["kind"] == "directory":
            value = filedialog.askdirectory(parent=self, title="Choose output folder")
        else:
            value = filedialog.askopenfilename(parent=self, title=spec["label"])
        if value:
            variable.set(value)

    def restore_defaults(self) -> None:
        self.draft = default_settings()
        for key, variable in self.variables.items():
            variable.set(self.draft[key] if isinstance(variable, tk.BooleanVar) else _display(self.draft[key]))
        for filename, editor in self.editors.items():
            editor.rows = copy.deepcopy(self.draft["conditions"][filename])
            editor.refresh()

    def collect(self) -> dict:
        config = copy.deepcopy(self.draft)
        for spec in FIELD_SPECS:
            value = self.variables[spec["key"]].get()
            try:
                if spec["kind"] == "int":
                    value = int(value)
                elif spec["kind"] == "float":
                    value = float(value)
                elif spec["kind"] != "bool":
                    value = str(value).strip()
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{spec['label']}: enter a valid {spec['kind']} value.") from exc
            config[spec["key"]] = value
        config["conditions"] = {filename: copy.deepcopy(editor.rows) for filename, editor in self.editors.items()}
        return validate_settings(config)

    def save(self) -> None:
        try:
            config = self.collect()
            save_settings(config)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Settings could not be saved", str(exc), parent=self)
            return
        self.app.config = config
        self.app.refresh_summary()
        self.app.status.set("Settings saved. Ready for the next session.")
        self.destroy()


class NeckerApp(tk.Tk):
    """Launcher UI. PsychoPy owns stimulus timing in a separate process."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Necker Studio")
        _apply_theme(self)
        _fit_window(self, 960, 760)
        self.handle = None
        self._launching = False
        self._closing = False
        self._stop_requested = False
        self._events: queue.Queue = queue.Queue()
        self._settings_dialog: SettingsDialog | None = None
        self._startup_error = None
        try:
            self.config = load_settings()
        except (ValueError, OSError) as exc:
            self.config = default_settings()
            self._startup_error = str(exc)
        self.status = tk.StringVar(self, "Ready to start a session.")
        self.output_text = tk.StringVar(self)
        self.setup_text = tk.StringVar(self)
        self.participant = {key: tk.StringVar(self) for key in ("participant_ID", "age", "sex", "handedness (left or right)")}
        self._create_menu()
        self._create_page()
        self.refresh_summary()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Control-comma>", lambda _event: self.open_settings())
        if self._startup_error:
            self.after_idle(self._show_startup_error)

    def _create_menu(self) -> None:
        menu = tk.Menu(self)
        self.file_menu = tk.Menu(menu, tearoff=False)
        self.file_menu.add_command(label="Settings…", accelerator="Ctrl+,", command=self.open_settings)
        self.file_menu.add_command(label="Open output folder", command=self.open_output)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.close)
        menu.add_cascade(label="File", menu=self.file_menu)
        self.configure(menu=menu)

    @staticmethod
    def _card(parent: tk.Misc, title: str, subtitle: str | None = None) -> ttk.Frame:
        outline = tk.Frame(parent, background=BORDER, padx=1, pady=1)
        outline.pack(fill="x", pady=(0, 14))
        content = ttk.Frame(outline, style="Card.TFrame", padding=18)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text=title, style="Heading.TLabel").pack(anchor="w")
        if subtitle:
            label = ttk.Label(content, text=subtitle, style="CardMuted.TLabel", wraplength=780)
            label.pack(anchor="w", pady=(5, 0))
            content.bind("<Configure>", lambda event: label.configure(wraplength=max(240, event.width - 36)), add="+")
        return content

    def _create_page(self) -> None:
        header = ttk.Frame(self, padding=(24, 20, 24, 15))
        header.pack(fill="x")
        brand = ttk.Frame(header)
        brand.pack(side="left")
        ttk.Label(brand, text="Necker Studio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(brand, text="Perception & conditioning", style="Muted.TLabel").pack(anchor="w", pady=(3, 0))
        self.settings_button = ttk.Button(header, text="Settings…", command=self.open_settings)
        self.settings_button.pack(side="right")
        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True, padx=(20, 14))
        self._main_scroll = scroll
        participant_card = self._card(scroll.content, "Participant", "Enter the session details before starting.")
        fields = ttk.Frame(participant_card, style="Card.TFrame")
        fields.pack(fill="x", pady=(14, 0))
        self.participant_controls = []
        for index, (key, label) in enumerate((("participant_ID", "Participant ID"), ("age", "Age"),
                                             ("sex", "Sex"), ("handedness (left or right)", "Handedness"))):
            fields.columnconfigure(index, weight=1, uniform="participants")
            ttk.Label(fields, text=label, style="Card.TLabel").grid(row=0, column=index, sticky="w", padx=(0, 10))
            if key.startswith("handedness"):
                control = ttk.Combobox(fields, textvariable=self.participant[key], values=("left", "right"), width=10)
            else:
                control = ttk.Entry(fields, textvariable=self.participant[key], width=10)
            control.grid(row=1, column=index, sticky="ew", padx=(0, 10), pady=(6, 0))
            self.participant_controls.append(control)
        summary = self._card(scroll.content, "Session sequence", "The original four stages, presented with PsychoPy.")
        metrics = ttk.Frame(summary, style="Card.TFrame")
        metrics.pack(fill="x", pady=(12, 5))
        self.count_labels = {}
        for index, (key, label) in enumerate((("practice", "01  Practice"), ("baseline", "02  Baseline"),
                                             ("conditioning", "03  Conditioning"), ("post", "04  Post-conditioning"))):
            metrics.columnconfigure(index, weight=1, uniform="metric")
            box = ttk.Frame(metrics, style="Card.TFrame")
            box.grid(row=0, column=index, sticky="nsew", padx=(0, 10))
            stage_label = ttk.Label(box, text=label, style="CardMuted.TLabel", wraplength=110)
            stage_label.pack(anchor="w")
            value = tk.StringVar(self, "—")
            self.count_labels[key] = value
            ttk.Label(box, textvariable=value, style="Metric.TLabel").pack(anchor="w", pady=(5, 0))
            ttk.Label(box, text="trials", style="CardMuted.TLabel").pack(anchor="w")
        ttk.Separator(summary).pack(fill="x", pady=12)
        setup = ttk.Label(summary, textvariable=self.setup_text, style="CardMuted.TLabel", wraplength=780)
        setup.pack(anchor="w")
        summary.bind("<Configure>", lambda event: setup.configure(wraplength=max(240, event.width - 36)), add="+")
        run = self._card(scroll.content, "Run session")
        run_help = ttk.Label(run, text="Use File > Settings to adjust the experiment. Press Escape in the experiment to stop.",
                            style="CardMuted.TLabel", wraplength=590)
        run_help.pack(anchor="w", pady=(5, 14))
        run.bind("<Configure>", lambda event: run_help.configure(wraplength=max(240, event.width - 36)))
        actions = ttk.Frame(run, style="Card.TFrame")
        actions.pack(fill="x")
        self.start_button = ttk.Button(actions, text="Start session", style="Primary.TButton", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(actions, text="Stop session", command=self.stop, state="disabled")
        self.stop_button.pack(side="left", padx=8)
        self.log_button = ttk.Button(actions, text="View run log", command=self.open_log, state="disabled")
        self.log_button.pack(side="right")
        output = self._card(scroll.content, "Session output")
        output_label = ttk.Label(output, textvariable=self.output_text, style="CardMuted.TLabel", wraplength=750)
        output_label.pack(anchor="w", pady=(6, 10))
        output.bind("<Configure>", lambda event: output_label.configure(wraplength=max(240, event.width - 36)), add="+")
        ttk.Button(output, text="Open output folder", command=self.open_output).pack(anchor="w")
        footer = ttk.Frame(self, padding=(24, 10, 24, 12))
        footer.pack(fill="x")
        self.badge = tk.Label(footer, text="READY", foreground=ACCENT, background="#dceeee", padx=9, pady=5,
                              font=("Segoe UI", 9, "bold"))
        self.badge.pack(side="left", padx=(0, 12))
        status = ttk.Label(footer, textvariable=self.status, style="Muted.TLabel", wraplength=660)
        status.pack(side="left", fill="x", expand=True)
        footer.bind("<Configure>", lambda event: status.configure(wraplength=max(250, event.width - 155)))

    def _show_startup_error(self) -> None:
        self.status.set("Saved settings need attention. Defaults are displayed.")
        messagebox.showerror("Saved settings could not be loaded", f"{self._startup_error}\n\n"
                             f"Default settings are displayed. Your file has not been changed:\n{SETTINGS_PATH}\n\n"
                             "Open File > Settings to review and save a valid configuration.", parent=self)

    def refresh_summary(self) -> None:
        counts = session_counts(self.config)
        for key, variable in self.count_labels.items():
            variable.set(str(counts[key]))
        serial = (f"Serial markers: {self.config['serial_port']} · {self.config['serial_baud']} baud"
                  if self.config["serial_enabled"] else "Serial markers: disabled")
        mode = "fullscreen" if self.config["full_screen"] else "windowed"
        self.setup_text.set(f"{counts['total']} trials total  ·  Display {self.config['screen']} ({mode})  ·  {serial}")
        self.output_text.set(str(runtime.output_directory(self.config)))

    def open_settings(self) -> None:
        if self.busy:
            return
        if self._settings_dialog is not None and self._settings_dialog.winfo_exists():
            self._settings_dialog.lift()
            return
        self._settings_dialog = SettingsDialog(self)

    @property
    def busy(self) -> bool:
        return self._launching or (self.handle is not None and self.handle.poll() is None)

    def _set_busy(self, busy: bool) -> None:
        self.start_button.configure(state="disabled" if busy else "normal")
        self.settings_button.configure(state="disabled" if busy else "normal")
        self.file_menu.entryconfigure(0, state="disabled" if busy else "normal")
        for control in self.participant_controls:
            control.configure(state="disabled" if busy else "normal")

    def start(self) -> None:
        if self.busy:
            return
        participant = {key: value.get().strip() for key, value in self.participant.items()}
        self._launching = True
        self._stop_requested = False
        self._set_busy(True)
        self.badge.configure(text="STARTING", foreground="#0c4a6e", background="#e0f2fe")
        self.status.set("Checking the PsychoPy engine and preparing the session…")
        config = copy.deepcopy(self.config)

        def launch() -> None:
            try:
                self._events.put(("started", runtime.start_session(config, participant)))
            except Exception as exc:
                self._events.put(("error", str(exc)))

        threading.Thread(target=launch, name="necker-session-launch", daemon=True).start()
        self.after(100, self._poll_launch)

    def _poll_launch(self) -> None:
        try:
            event, value = self._events.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_launch)
            return
        self._launching = False
        if event == "error":
            self._set_busy(False)
            self.badge.configure(text="ATTENTION", foreground="#9a3412", background="#ffedd5")
            self.status.set("The session did not start. Review the error and settings.")
            messagebox.showerror("Unable to start session", value, parent=self)
            if self._closing:
                self.destroy()
            return
        self.handle = value
        self.log_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        self.badge.configure(text="RUNNING", foreground=ACCENT, background="#dceeee")
        self.status.set("Session running. PsychoPy controls the presentation window.")
        self.output_text.set(str(self.handle.session_dir))
        if self._closing:
            self.stop()
        self.after(300, self._poll_session)

    def _poll_session(self) -> None:
        code = self.handle.poll()
        if code is None:
            self.after(300, self._poll_session)
            return
        self._set_busy(False)
        self.stop_button.configure(state="disabled")
        result = {}
        try:
            result = json.loads(self.handle.result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        if not isinstance(result, dict):
            result = {}
        status = result.get("status", "failed")
        if status == "completed":
            self.badge.configure(text="COMPLETE", foreground="#166534", background="#dcfce7")
            self.status.set("Session complete. Data and settings are in the session output folder.")
        elif status == "aborted":
            self.badge.configure(text="STOPPED", foreground="#9a3412", background="#ffedd5")
            self.status.set("Session stopped. Available data are in the session output folder.")
        else:
            self.badge.configure(text="FAILED", foreground="#991b1b", background="#fef2f2")
            self.status.set("The session ended with an error. Open the run log for details.")
            error = result.get("error") or f"The PsychoPy process exited without a completion report (exit code {code})."
            messagebox.showerror("Session error", f"{error}\n\nRun log:\n{self.handle.log_path}", parent=self)
        if self._closing:
            self.destroy()

    def stop(self) -> None:
        if self.handle is None or self.handle.poll() is not None or self._stop_requested:
            return
        try:
            self.handle.request_stop()
        except OSError as exc:
            messagebox.showerror("Stop request could not be saved", f"{exc}\n\nPress Escape in the experiment window to stop.", parent=self)
            return
        self._stop_requested = True
        self.stop_button.configure(state="disabled")
        self.badge.configure(text="STOPPING", foreground="#9a3412", background="#ffedd5")
        self.status.set("Stop requested. Waiting for PsychoPy to save data and close…")

    def open_output(self) -> None:
        try:
            path = Path(self.output_text.get())
            path.mkdir(parents=True, exist_ok=True)
            _open_path(path)
        except OSError as exc:
            messagebox.showerror("Unable to open output folder", str(exc), parent=self)

    def open_log(self) -> None:
        if self.handle is not None:
            try:
                _open_path(self.handle.log_path)
            except OSError as exc:
                messagebox.showerror("Unable to open run log", str(exc), parent=self)

    def close(self) -> None:
        if self.busy:
            if self._closing:
                return
            if messagebox.askyesno("Stop and close?", "A session is active. Request a safe stop, wait for data to save, and close Necker Studio?", parent=self):
                self._closing = True
                self.stop()
            return
        self.destroy()


def main() -> None:
    app = NeckerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
