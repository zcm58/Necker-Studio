"""Validated application settings; no PsychoPy or spreadsheet dependency.

The bundled defaults reproduce ``__NEW_NECKER.psyexp``. Editable condition
tables are ordinary JSON data; no cell or settings value is evaluated as code.
"""

from __future__ import annotations

from copy import deepcopy
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


APP_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = APP_DIR / "settings.json"
DEFAULTS_PATH = APP_DIR / "defaults.json"
ASSETS_DIR = APP_DIR / "assets"
SERIAL_PORT = "COM3"


def _field(key, label, group, kind, default, minimum=None, maximum=None, help="", choices=None):
    result = {"key": key, "label": label, "group": group, "kind": kind,
              "default": default, "min": minimum, "max": maximum, "help": help}
    if choices is not None:
        result["choices"] = choices
    return result


FIELD_SPECS = [
    _field("psychopy_python", "PsychoPy Python", "General", "file", "",
           help="Leave blank to find an installed PsychoPy Python automatically, or choose its python.exe."),
    _field("output_dir", "Results folder", "General", "directory", "data",
           help="Saved across launches. Relative folders are inside Necker Studio. Each session creates its own folder here."),
    _field("sophia_mode", "Sophia Mode: confirm BioSemi recording", "General", "bool", True,
           help="Before each launch, require the administrator to check that BioSemi is recording and type Confirm. This is an operator check, not automatic recording detection."),
    _field("full_screen", "Full screen", "Display", "bool", True,
           help="Present the experiment full screen, as in the reference project."),
    _field("window_width", "Window width (pixels)", "Display", "int", 1920, 64, 16384,
           "Window resolution; also used for monitor pixel size when calibration is overridden."),
    _field("window_height", "Window height (pixels)", "Display", "int", 1080, 64, 16384),
    _field("screen", "Display number", "Display", "int", 1, 1, 32,
           "1 is the first display; PsychoPy receives the corresponding zero-based screen index."),
    _field("monitor_name", "PsychoPy monitor", "Display", "str", "testMonitor",
           help="Name of the existing PsychoPy monitor calibration used for visual degrees."),
    _field("monitor_width_cm", "Monitor width (cm; optional)", "Display", "str", "", 1, 1000,
           "Leave both calibration overrides blank to use the saved monitor. Otherwise supply both values."),
    _field("monitor_distance_cm", "Viewing distance (cm; optional)", "Display", "str", "", 1, 10000,
           "Distance from the viewer's eyes to the screen. Required with a monitor width override."),
    _field("cube_width_deg", "Cube width (degrees)", "Display", "float", 6.0, 0.01, 180),
    _field("cube_height_deg", "Cube height (degrees)", "Display", "float", 5.25, 0.01, 180),
    _field("volume", "Sound volume (0–1)", "Audio & triggers", "float", 1.0, 0, 1),
    _field("serial_enabled", "Enable serial triggers", "Audio & triggers", "bool", True,
           help="Enabled in the reference. Disable only for sessions that do not use the trigger device."),
    _field("serial_port", "Serial port (locked)", "Audio & triggers", "str", SERIAL_PORT,
           help="Fixed to COM3 for this experiment; this field cannot be edited."),
    _field("serial_baud", "Serial baud rate", "Audio & triggers", "int", 115200, 1, 4000000),
    _field("practice_reps", "Practice repetitions", "Trial counts", "int", 1, 0, 10000,
           "Repetitions of all ambiguous-cube conditions; original default is 8 practice trials."),
    _field("baseline_blocks", "Baseline blocks", "Trial counts", "int", 5, 0, 10000),
    _field("baseline_reps", "Baseline repetitions per block", "Trial counts", "int", 3, 0, 10000),
    _field("conditioning_blocks", "Conditioning blocks", "Trial counts", "int", 5, 0, 10000),
    _field("conditioning_reps", "Conditioning repetitions per block", "Trial counts", "int", 4, 0, 10000),
    _field("post_blocks", "Post-conditioning blocks", "Trial counts", "int", 5, 0, 10000),
    _field("post_reps", "Post-conditioning repetitions per block", "Trial counts", "int", 3, 0, 10000),
    _field("no_go_demo_reps", "No-go demonstration repetitions", "Trial counts", "int", 1, 0, 10000,
           "Sequential repetitions of the first three demonstration conditions."),
    _field("go_demo_reps", "Go demonstration repetitions", "Trial counts", "int", 2, 0, 10000,
           "Repetitions of the fourth demonstration condition."),
    _field("stimulus_seconds", "Cube exposure (seconds)", "Timing", "float", 0.15, 0.001, 600),
    _field("practice_seconds", "Practice routine (seconds)", "Timing", "float", 0.8, 0.001, 600),
    _field("necker_seconds", "Ambiguous-cube routine (seconds)", "Timing", "float", 1.5, 0.001, 600),
    _field("response_seconds", "Choice response (seconds)", "Timing", "float", 3.0, 0.001, 600),
    _field("conditioning_seconds", "Conditioning routine (seconds)", "Timing", "float", 1.5, 0.001, 600),
    _field("gonogo_seconds", "Go/no-go response (seconds)", "Timing", "float", 1.4, 0.001, 600),
    _field("fixation_seconds", "Fixation (seconds)", "Timing", "float", 1.0, 0.001, 600),
    _field("blank_min_frames", "Blank minimum (frames)", "Timing", "int", 62, 1, 100000,
           "Retains the original per-frame random stop test; the upper bound is exclusive."),
    _field("blank_max_frames", "Blank upper bound (exclusive)", "Timing", "int", 125, 2, 100001),
    _field("tone_seconds", "Tone component duration (seconds)", "Timing", "float", 0.05, 0.001, 1.8,
           "At most 1.8 seconds to fit the fixed no-go demonstrations (2.2-second routine, sound starts at 0.4 seconds). The original WAV recordings remain unchanged."),
]

CONDITION_COLUMNS = {
    "LorR.xlsx": ["Sound", "delay", "image", "choice", "ISI"],
    "SoundA.xlsx": ["Sound", "text", "image", "choice", "correct", "GoNoGo"],
    "SoundEx.xlsx": ["Sound", "text", "image"],
}

# Useful to a condition-table editor; columns keep the original Builder names.
CONDITION_CHOICES = {"correct": ["Left", "Right"], "GoNoGo": ["None", "space"]}
CONDITION_HELP = {
    "LorR.xlsx": "Conditions shared by practice, baseline and post-conditioning. The image and ISI columns are retained as metadata; the reference draws the fixed Necker6.png cube and does not use these columns.",
    "SoundA.xlsx": "Conditioning conditions. The correct and GoNoGo columns are retained as metadata and do not score responses in the reference. Original values are Left/Right for correct and the literal text None/space for GoNoGo.",
    "SoundEx.xlsx": "Exactly four sequential demonstration conditions: rows 1–3 are no-go examples; row 4 is the go example.",
}


def default_settings() -> dict[str, Any]:
    """Return a fresh copy of the bundled reference settings and condition rows."""
    try:
        return json.loads(DEFAULTS_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Cannot read bundled defaults at {DEFAULTS_PATH}: {exc}") from exc


def _number(value, label, minimum, maximum, integer=False):
    accepted = type(value) is int if integer else type(value) in (int, float)
    if not accepted or (type(value) is float and not math.isfinite(value)):
        name = "whole number" if integer else "finite number"
        raise ValueError(f"{label} must be a {name}.")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label} must be no greater than {maximum}.")
    return value


def _string(value, label, allow_empty=False):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text.")
    if "\x00" in value:
        raise ValueError(f"{label} contains an invalid null character.")
    if not allow_empty and not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value


def _existing_file(value, label, relative_to):
    _string(value, label)
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = relative_to / path
    try:
        exists = path.is_file()
    except (OSError, ValueError) as exc:
        raise ValueError(f"{label} is not a valid file path: {value}") from exc
    if not exists:
        raise ValueError(f"{label} file does not exist: {path}")


def validate_settings(config: dict[str, Any]) -> dict[str, Any]:
    """Validate all settings and return a detached copy with calibrated numbers.

    Numeric configuration values are strictly typed: strings and booleans do
    not stand in for numbers. Optional calibration fields are the exception:
    they accept blank text or a number entered through their text controls.
    """
    if not isinstance(config, dict):
        raise ValueError("Settings must contain a JSON object.")
    expected = {spec["key"] for spec in FIELD_SPECS} | {"schema_version", "conditions"}
    missing, extra = expected - config.keys(), config.keys() - expected
    if missing:
        raise ValueError("Settings are missing: " + ", ".join(sorted(missing)))
    if extra:
        raise ValueError("Unknown settings: " + ", ".join(sorted(map(str, extra))))
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("Unsupported settings schema. This version requires schema_version 1.")
    result = deepcopy(config)
    for spec in FIELD_SPECS:
        key, kind, label = spec["key"], spec["kind"], spec["label"]
        value = result[key]
        if key in ("monitor_width_cm", "monitor_distance_cm"):
            if isinstance(value, str):
                value = value.strip()
                if value:
                    try:
                        value = float(value)
                    except ValueError as exc:
                        raise ValueError(f"{label} must be blank or a positive number.") from exc
            if value != "":
                value = _number(value, label, spec["min"], spec["max"])
            result[key] = value
        elif kind == "bool":
            if type(value) is not bool:
                raise ValueError(f"{label} must be enabled or disabled.")
        elif kind in ("int", "float"):
            _number(value, label, spec["min"], spec["max"], integer=kind == "int")
        else:
            _string(value, label, allow_empty=key == "psychopy_python")
            if kind == "choice" and value not in spec["choices"]:
                raise ValueError(f"{label} must be one of: {', '.join(spec['choices'])}.")
            if key == "psychopy_python" and value:
                _existing_file(value, label, APP_DIR)
            if kind == "directory":
                directory = Path(value).expanduser()
                if not directory.is_absolute():
                    directory = APP_DIR / directory
                try:
                    if directory.exists() and not directory.is_dir():
                        raise ValueError(f"{label} must be a directory: {directory}")
                except OSError as exc:
                    raise ValueError(f"{label} is not a valid directory path: {value}") from exc
    if result["serial_port"] != SERIAL_PORT:
        raise ValueError(f"Serial port is locked to {SERIAL_PORT} for this experiment.")
    if (result["monitor_width_cm"] == "") != (result["monitor_distance_cm"] == ""):
        raise ValueError("Set both monitor width and viewing distance, or leave both blank to use the saved monitor calibration.")
    if result["blank_min_frames"] >= result["blank_max_frames"]:
        raise ValueError("Blank upper bound must be greater than the blank minimum; the upper bound is exclusive.")
    for key, label in (("practice_seconds", "Practice routine"),
                       ("conditioning_seconds", "Conditioning routine"),
                       ("necker_seconds", "Ambiguous-cube routine")):
        if result[key] < result["stimulus_seconds"]:
            raise ValueError(f"{label} must last at least as long as the cube exposure ({result['stimulus_seconds']:g} seconds).")
    if result["conditioning_seconds"] < result["tone_seconds"]:
        raise ValueError(f"Conditioning routine must last at least as long as its tone ({result['tone_seconds']:g} seconds).")

    tables = result["conditions"]
    if not isinstance(tables, dict) or set(tables) != set(CONDITION_COLUMNS):
        raise ValueError("Conditions must contain exactly LorR.xlsx, SoundA.xlsx, and SoundEx.xlsx.")
    for filename, columns in CONDITION_COLUMNS.items():
        rows = tables[filename]
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"{filename} must contain at least one condition row.")
        if filename == "SoundEx.xlsx" and len(rows) != 4:
            raise ValueError("SoundEx.xlsx must contain exactly four rows: three no-go examples and one go example.")
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict) or set(row) != set(columns):
                raise ValueError(f"{filename}, row {index}: columns must be {', '.join(columns)}.")
            for column, value in row.items():
                label = f"{filename}, row {index}, {column}"
                if column == "ISI":
                    # Preserve blank source-workbook values as None.
                    if value == "" or value is None:
                        row[column] = None
                    else:
                        _number(value, label, 0, 600)
                elif column == "delay":
                    _number(value, label, 0, 600)
                elif column in ("Sound", "image", "choice"):
                    _existing_file(value, label, ASSETS_DIR)
                else:
                    _string(value, label)
                    if column in CONDITION_CHOICES and value not in CONDITION_CHOICES[column]:
                        raise ValueError(f"{label} must be one of: {', '.join(CONDITION_CHOICES[column])}.")
    latest_tone_end = max(row["delay"] for row in tables["LorR.xlsx"]) + result["tone_seconds"]
    if result["necker_seconds"] + 1e-9 < latest_tone_end:
        raise ValueError(
            f"Ambiguous-cube routine must last at least {latest_tone_end:g} seconds "
            "so the latest condition tone can finish (sound delay plus tone duration)."
        )
    return result


def load_settings(path=SETTINGS_PATH) -> dict[str, Any]:
    """Load saved settings, or reference defaults if no settings file exists."""
    path = Path(path)
    if not path.exists():
        return validate_settings(default_settings())
    try:
        config = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Cannot read settings at {path}: {exc}") from exc
    try:
        # Add this new launch safeguard to older saved configurations without
        # resetting the output directory, calibration, or protocol settings.
        if isinstance(config, dict) and config.get("schema_version") == 1:
            config.setdefault("sophia_mode", True)
        return validate_settings(config)
    except ValueError as exc:
        raise ValueError(f"Invalid settings in {path}: {exc}") from exc


def save_settings(config: dict[str, Any], path=SETTINGS_PATH) -> dict[str, Any]:
    """Validate and atomically save settings; return the validated copy."""
    validated = validate_settings(config)
    path = Path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(validated, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except (OSError, ValueError) as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise ValueError(f"Cannot save settings at {path}: {exc}") from exc
    return validated


def condition_rows(config, filename, selection=None):
    """Copy a condition table or the fixed reference demonstration subsets.

    Selection is deliberately limited to the two subsets used by the source
    experiment; it is never parsed or evaluated as Python.
    """
    if filename not in CONDITION_COLUMNS:
        raise ValueError(f"Unknown condition table: {filename}")
    rows = deepcopy(config["conditions"][filename])
    if selection is None or selection == "":
        return rows
    if selection == "0:3":
        return rows[:3]
    if selection == "3":
        if len(rows) < 4:
            raise ValueError(f"{filename} needs a fourth row for the go demonstration.")
        return [rows[3]]
    raise ValueError(f"Unsupported condition selection: {selection!r}")


def session_counts(config):
    """Return main-trial counts, including practice and excluding demonstrations."""
    ambiguous = len(config["conditions"]["LorR.xlsx"])
    conditioning = len(config["conditions"]["SoundA.xlsx"])
    counts = {
        "practice": ambiguous * config["practice_reps"],
        "baseline": ambiguous * config["baseline_blocks"] * config["baseline_reps"],
        "conditioning": conditioning * config["conditioning_blocks"] * config["conditioning_reps"],
        "post": ambiguous * config["post_blocks"] * config["post_reps"],
    }
    counts["total"] = sum(counts.values())
    return counts
