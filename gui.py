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
    from .window_layout import fit_window as _fit_window
    from .participant import HANDEDNESS_KEY, HANDEDNESS_VALUES, SEX_VALUES, ParticipantError, validate_participant, recording_confirmation_required
    from .settings import (
        APP_DIR, APP_NAME, CONDITION_CHOICES, CONDITION_COLUMNS,
        FIELD_SPECS, SETTINGS_PATH, default_settings, load_settings,
        save_settings, session_counts, validate_settings, serial_triggers_enabled,
    )
else:
    import runtime
    from window_layout import fit_window as _fit_window
    from participant import HANDEDNESS_KEY, HANDEDNESS_VALUES, SEX_VALUES, ParticipantError, validate_participant, recording_confirmation_required
    from settings import (
        APP_DIR, APP_NAME, CONDITION_CHOICES, CONDITION_COLUMNS,
        FIELD_SPECS, SETTINGS_PATH, default_settings, load_settings,
        save_settings, session_counts, validate_settings, serial_triggers_enabled,
    )


PAGE = "#f4f7fb"
SURFACE = "#ffffff"
INK = "#1f2f44"
MUTED = "#53677d"
BORDER = "#d7dfea"
ACCENT = "#087e83"


def _apply_theme(root: tk.Tk) -> None:
    root.configure(background=PAGE)
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
    style.map("TEntry", fieldbackground=[("disabled", "#e4e8ed")],
              foreground=[("disabled", "#687585")])
    style.configure("TCombobox", padding=6, fieldbackground=SURFACE)
    style.configure("TCheckbutton", background=PAGE, padding=(0, 4))
    style.configure("TNotebook", background=PAGE, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(12, 8))
    style.map("TNotebook.Tab", background=[("selected", SURFACE)])
    style.layout("Sections.TNotebook.Tab", [])
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, rowheight=29)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=6)
    style.map("Treeview", background=[("selected", "#d8eeee")],
              foreground=[("selected", INK)])


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
        self.winfo_toplevel().bind("<FocusIn>", self._reveal_focus, add="+")

    def _reveal_focus(self, event: tk.Event) -> None:
        if not self.winfo_exists() or not str(event.widget).startswith(str(self.content) + "."):
            return
        widget = event.widget
        top = widget.winfo_rooty() - self.content.winfo_rooty()
        visible_top = self.canvas.canvasy(0)
        height = self.canvas.winfo_height()
        bottom = top + widget.winfo_height()
        target = top - 8 if top < visible_top else bottom - height + 8
        if top < visible_top or bottom > visible_top + height:
            self.canvas.yview_moveto(max(0, target) / max(1, self.content.winfo_height()))

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


class FlowButtons(ttk.Frame):
    """Wrap actions onto another row when screen scaling leaves less space."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.buttons = []
        self.bind("<Configure>", self._layout)

    def add(self, text, command, **kwargs):
        button = ttk.Button(self, text=text, command=command, **kwargs)
        self.buttons.append(button)
        self.after_idle(self._layout)
        return button

    def _layout(self, _event=None):
        if not self.winfo_exists():
            return
        available = max(1, self.winfo_width() - 36)
        row = column = used = 0
        for button in self.buttons:
            width = button.winfo_reqwidth() + 8
            if used and used + width > available:
                row, column, used = row + 1, 0, 0
            button.grid(row=row, column=column, sticky="w", padx=(0, 8), pady=3)
            column += 1
            used += width


def _section_selector(parent, notebook, labels):
    selector = ttk.Combobox(parent, values=labels, state="readonly", width=1)
    selector.pack(fill="x", pady=(8, 10))
    selector.current(0)
    selector.bind("<<ComboboxSelected>>", lambda _event: notebook.select(selector.current()))
    notebook.bind("<<NotebookTabChanged>>", lambda _event: selector.current(notebook.index("current")))
    return selector


class ParticipantDialog(tk.Toplevel):
    """Fresh, validated demographics for each click of Launch Experiment."""

    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("Participant Information")
        self.configure(background=PAGE)
        self.transient(parent)
        _fit_window(self, 700, 600)
        footer = FlowButtons(self, padding=(18, 8, 18, 12))
        footer.pack(side="bottom", fill="x")
        self.continue_button = footer.add("Continue", self.accept, style="Primary.TButton")
        footer.add("Cancel", self.destroy)
        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True, padx=18, pady=12)
        content = scroll.content
        content.columnconfigure(0, weight=1)
        self.variables = {}
        self.controls = {}
        fields = (
            ("participant_ID", "Participant number", None),
            ("age", "Age", None),
            ("sex", "Sex", SEX_VALUES),
            (HANDEDNESS_KEY, "Handedness", HANDEDNESS_VALUES),
            ("colorblind", "Colorblind", ("No", "Yes")),
            ("manual_removed_electrodes", "Manually removed electrodes (optional)", None),
        )
        labels = []
        for index, (key, label, choices) in enumerate(fields):
            caption = ttk.Label(content, text=label, wraplength=550)
            caption.grid(row=index * 2, column=0, sticky="ew", pady=(10, 4))
            labels.append(caption)
            variable = self.variables[key] = tk.StringVar(self)
            if choices:
                control = ttk.Combobox(content, textvariable=variable, values=choices, state="readonly", width=1)
            else:
                control = ttk.Entry(content, textvariable=variable, width=1)
                if key in {"participant_ID", "age"}:
                    check = self.register(lambda value: not value or (value.isascii() and value.isdigit()))
                    control.configure(validate="key", validatecommand=(check, "%P"))
            control.grid(row=index * 2 + 1, column=0, sticky="ew")
            self.controls[key] = control
        self.error_text = tk.StringVar(self)
        error = ttk.Label(self, textvariable=self.error_text, foreground="#9a3412", wraplength=550)
        error.pack(side="bottom", fill="x", padx=24, pady=(0, 8), before=scroll)
        error.bind("<Configure>", lambda event: error.configure(wraplength=max(80, event.width)))
        content.bind("<Configure>", lambda event: [label.configure(wraplength=max(80, event.width - 20)) for label in labels], add="+")
        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Return>", lambda _event: self.accept())
        self.grab_set()
        self.after_idle(self.controls["participant_ID"].focus_set)

    def accept(self):
        values = {key: variable.get() for key, variable in self.variables.items()}
        values["colorblind"] = {"No": False, "Yes": True}.get(values["colorblind"])
        try:
            self.result = validate_participant(values)
        except ParticipantError as exc:
            self.error_text.set(str(exc))
            self.controls[exc.field].focus_set()
            return
        self.destroy()

    def show(self):
        self.wait_window()
        return self.result


class BioSemiRecordingConfirmationDialog(tk.Toplevel):
    """FPVS Sophia Mode: a new typed operator confirmation for every launch."""

    def __init__(self, parent):
        super().__init__(parent)
        self.result = False
        self.title("Sophia Mode Recording Check")
        self.configure(background=PAGE)
        self.transient(parent)
        _fit_window(self, 700, 260)
        footer = FlowButtons(self, padding=(18, 8, 18, 12))
        footer.pack(side="bottom", fill="x")
        self.continue_button = footer.add("Continue", self.accept, style="Primary.TButton", state="disabled")
        footer.add("Cancel", self.destroy)
        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        prompt = ttk.Label(scroll.content, text="Confirm BioSemi is recording. Type Confirm to continue.", wraplength=600)
        prompt.pack(fill="x", pady=(0, 18))
        self.confirmation = tk.StringVar(self)
        self.entry = ttk.Entry(scroll.content, textvariable=self.confirmation, width=1)
        self.entry.pack(fill="x")
        scroll.content.bind("<Configure>", lambda event: prompt.configure(wraplength=max(80, event.width - 20)), add="+")
        self.confirmation.trace_add("write", lambda *_args: self.continue_button.configure(state="normal" if self.matches() else "disabled"))
        self.bind("<Return>", lambda _event: self.accept())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()
        self.after_idle(self.entry.focus_set)

    def matches(self):
        return self.confirmation.get().strip().casefold() == "confirm"

    def accept(self):
        if self.matches():
            self.result = True
            self.destroy()

    def show(self):
        self.wait_window()
        return self.result


class ConditionEditor(ttk.Frame):
    """A staged condition-table editor; no workbook changes are needed."""

    def __init__(self, parent: tk.Misc, filename: str, rows: list[dict]) -> None:
        super().__init__(parent, padding=12)
        self.filename = filename
        self.columns = list(CONDITION_COLUMNS[filename])
        self.rows = copy.deepcopy(rows)
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, columns=self.columns, show="headings", selectmode="browse", height=7)
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
        actions = FlowButtons(self)
        actions.pack(fill="x", pady=(10, 0))
        actions.add("Edit row…", self.edit_row)
        if filename != "SoundEx.xlsx":
            actions.add("Add", self.add_row)
            actions.add("Duplicate", self.duplicate_row)
            actions.add("Remove", self.remove_row)
        actions.add("↑", lambda: self.move_row(-1), width=3)
        actions.add("↓", lambda: self.move_row(1), width=3)
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
        scroll.content.columnconfigure(0, weight=1)
        variables = {}
        for row_index, column in enumerate(self.columns):
            ttk.Label(scroll.content, text=column).grid(row=row_index * 2, column=0, columnspan=2, sticky="w", pady=(8, 4))
            variable = tk.StringVar(dialog, value=_display(source.get(column)))
            variables[column] = variable
            if column in CONDITION_CHOICES:
                entry = ttk.Combobox(scroll.content, textvariable=variable,
                                     values=CONDITION_CHOICES[column], state="readonly", width=1)
            else:
                entry = ttk.Entry(scroll.content, textvariable=variable, width=1)
            entry.grid(row=row_index * 2 + 1, column=0, sticky="ew")
            if column in {"image", "Sound", "choice"}:
                ttk.Button(scroll.content, text="Browse…", command=lambda v=variable: self._browse_asset(v, dialog)).grid(
                    row=row_index * 2 + 1, column=1, padx=(7, 0))

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
        footer.pack(side="bottom", fill="x", before=scroll)
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
        self.title(f"{APP_NAME} — Settings")
        self.configure(background=PAGE)
        self.transient(parent)
        _fit_window(self, 960, 710)
        header = ttk.Frame(self, padding=(20, 16, 20, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Experiment settings", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        self.notebook = ttk.Notebook(self, style="Sections.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=18)
        groups: dict[str, ScrollFrame] = {}
        for spec in FIELD_SPECS:
            group = spec["group"]
            if group not in groups:
                groups[group] = ScrollFrame(self.notebook)
                self.notebook.add(groups[group], text=group)
            self._field(groups[group].content, spec)
        conditions_page = ScrollFrame(self.notebook)
        self.notebook.add(conditions_page, text="Conditions")
        conditions = ttk.Notebook(conditions_page.content, style="Sections.TNotebook")
        _section_selector(conditions_page.content, conditions, [name.removesuffix(".xlsx") for name in CONDITION_COLUMNS])
        conditions.pack(fill="both", expand=True)
        for filename in CONDITION_COLUMNS:
            editor = ConditionEditor(conditions, filename, self.draft["conditions"][filename])
            self.editors[filename] = editor
            conditions.add(editor, text=filename.removesuffix(".xlsx"))
        self.section_selector = _section_selector(header, self.notebook, list(groups) + ["Conditions"])
        footer = self.footer = FlowButtons(self, padding=(18, 12, 18, 16))
        footer.pack(side="bottom", fill="x", before=self.notebook)
        footer.add("Save settings", self.save, style="Primary.TButton")
        footer.add("Cancel", self.destroy)
        footer.add("Restore defaults", self.restore_defaults)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    def _field(self, parent: ttk.Frame, spec: dict) -> None:
        frame = ttk.Frame(parent, padding=(12, 8))
        frame.pack(fill="x")
        frame.columnconfigure(0, weight=1)
        key, kind = spec["key"], spec["kind"]
        variable = (tk.BooleanVar(self, value=self.draft[key]) if kind == "bool"
                    else tk.StringVar(self, value=_display(self.draft[key])))
        self.variables[key] = variable
        labels = []
        if kind == "bool":
            frame.columnconfigure(0, weight=0)
            frame.columnconfigure(1, weight=1)
            ttk.Checkbutton(frame, variable=variable).grid(row=0, column=0, sticky="nw")
            label = ttk.Label(frame, text=spec["label"], wraplength=500)
            label.grid(row=0, column=1, sticky="ew")
            label.bind("<Button-1>", lambda _event: variable.set(not variable.get()))
            labels.append(label)
        else:
            label = ttk.Label(frame, text=spec["label"], wraplength=500)
            label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
            labels.append(label)
            if spec.get("choices"):
                control = ttk.Combobox(frame, textvariable=variable, values=spec["choices"], state="readonly", width=1)
            else:
                control = ttk.Entry(frame, textvariable=variable, width=1)
            if key == "serial_port":
                control.configure(state="disabled", takefocus=False)
                self.serial_port_control = control
            control.grid(row=1, column=0, sticky="ew")
            if kind in {"path", "directory", "file"} or key in {"psychopy_python", "output_dir"}:
                ttk.Button(frame, text="Browse…", command=lambda k=key, v=variable, s=spec: self._browse(k, v, s)).grid(
                    row=1, column=1, padx=(8, 0))
        frame.bind("<Configure>", lambda event: [label.configure(wraplength=max(80, event.width - 60)) for label in labels])

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
        self.app.status.set("Settings saved.")
        self.destroy()


class NeckerApp(tk.Tk):
    """Launcher UI. PsychoPy owns stimulus timing in a separate process."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
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
        self.status = tk.StringVar(self)
        self.output_text = tk.StringVar(self)
        self.setup_text = tk.StringVar(self)
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
    def _card(parent: tk.Misc, title: str) -> ttk.Frame:
        outline = tk.Frame(parent, background=BORDER, padx=1, pady=1)
        outline.pack(fill="x", pady=(0, 14))
        content = ttk.Frame(outline, style="Card.TFrame", padding=18)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text=title, style="Heading.TLabel").pack(anchor="w")
        return content

    def _create_page(self) -> None:
        header = ttk.Frame(self, padding=(24, 20, 24, 15))
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)
        brand = ttk.Frame(header)
        brand.grid(row=0, column=0, sticky="ew")
        title = ttk.Label(brand, text=APP_NAME, style="Title.TLabel", wraplength=700)
        title.pack(fill="x")
        brand.bind("<Configure>", lambda event: title.configure(wraplength=max(80, event.width - 8)))
        self.settings_button = ttk.Button(header, text="Settings…", command=self.open_settings)
        self.settings_button.grid(row=0, column=1, sticky="ne", padx=(16, 0))
        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True, padx=(20, 14))
        self._main_scroll = scroll
        summary = self._card(scroll.content, "Session sequence")
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
        summary.bind("<Configure>", lambda event: setup.configure(wraplength=max(240, event.width - 44)), add="+")
        run = self._card(scroll.content, "Run session")
        actions = ttk.Frame(run, style="Card.TFrame")
        actions.pack(fill="x", pady=(12, 0))
        self.start_button = ttk.Button(actions, text="Launch Experiment", style="Primary.TButton", command=self.start)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(actions, text="Stop session", command=self.stop, state="disabled")
        self.stop_button.pack(side="left", padx=8)
        self.log_button = ttk.Button(actions, text="View run log", command=self.open_log, state="disabled")
        self.log_button.pack(side="right")
        output = self._card(scroll.content, "Session output")
        output_label = ttk.Label(output, textvariable=self.output_text, style="CardMuted.TLabel", wraplength=750)
        output_label.pack(anchor="w", pady=(6, 10))
        output.bind("<Configure>", lambda event: output_label.configure(wraplength=max(240, event.width - 44)), add="+")
        ttk.Button(output, text="Open output folder", command=self.open_output).pack(anchor="w")
        footer = ttk.Frame(self, padding=(24, 10, 24, 12))
        footer.pack(side="bottom", fill="x", before=scroll)
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
                  if serial_triggers_enabled(self.config) else "Serial markers: disabled")
        mode = "fullscreen" if self.config["full_screen"] else "windowed"
        prefix = "TEST MODE  ·  " if self.config["test_mode"] else ""
        self.setup_text.set(f"{prefix}{counts['total']} trials total  ·  Display {self.config['screen']} ({mode})  ·  {serial}")
        self.output_text.set(str(runtime.output_directory(self.config)))
        test_mode = self.config["test_mode"]
        self.start_button.configure(text="Launch Test Experiment" if test_mode else "Launch Experiment")
        self.badge.configure(text="TEST MODE" if test_mode else "READY",
                             foreground="#9a3412" if test_mode else ACCENT,
                             background="#ffedd5" if test_mode else "#dceeee")

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

    def _participant_details(self):
        return ParticipantDialog(self).show()

    def _confirm_recording(self):
        return BioSemiRecordingConfirmationDialog(self).show()

    def _confirm_test_mode(self):
        return messagebox.askyesno(
            "Launch test experiment?",
            "Launch a test experiment without COM3 or BioSemi recording?", parent=self,
        )

    def start(self) -> None:
        if self.busy:
            return
        self._launching = True
        self._set_busy(True)
        try:
            config = validate_settings(copy.deepcopy(self.config))
            if config["test_mode"]:
                if not self._confirm_test_mode():
                    self.status.set("Test launch cancelled.")
                    return
                participant = None
            else:
                participant = self._participant_details()
                if participant is None:
                    self.status.set("Launch cancelled.")
                    return
            needs_recording = recording_confirmation_required(config)
            recording_confirmed = needs_recording and self._confirm_recording()
            if needs_recording and not recording_confirmed:
                self.status.set("Launch cancelled at the BioSemi recording check.")
                return
        except ValueError as exc:
            messagebox.showerror("Unable to start session", str(exc), parent=self)
            return
        finally:
            self._launching = False
            self._set_busy(False)
        self._launching = True
        self._stop_requested = False
        self._set_busy(True)
        self.badge.configure(text="STARTING", foreground="#0c4a6e", background="#e0f2fe")
        self.status.set("Starting session…")

        def launch() -> None:
            try:
                self._events.put(("started", runtime.start_session(config, participant, recording_confirmed=recording_confirmed)))
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
            self.status.set("Session could not start.")
            messagebox.showerror("Unable to start session", value, parent=self)
            if self._closing:
                self.destroy()
            return
        self.handle = value
        self.log_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        self.badge.configure(text="TEST RUN" if self.config["test_mode"] else "RUNNING", foreground=ACCENT, background="#dceeee")
        self.status.set("Test session running." if self.config["test_mode"] else "Session running.")
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
            self.status.set("Session complete.")
        elif status == "aborted":
            self.badge.configure(text="STOPPED", foreground="#9a3412", background="#ffedd5")
            self.status.set("Session stopped.")
        else:
            self.badge.configure(text="FAILED", foreground="#991b1b", background="#fef2f2")
            self.status.set("Session failed. See run log.")
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
        self.status.set("Stopping and saving data…")

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
            if messagebox.askyesno("Stop and close?", f"A session is active. Request a safe stop, wait for data to save, and close {APP_NAME}?", parent=self):
                self._closing = True
                self.stop()
            return
        self.destroy()


def main() -> None:
    app = NeckerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
