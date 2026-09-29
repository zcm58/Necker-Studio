"""Separate installed resources from per-user settings and experiment output."""
import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent


def state_directory(app_dir=APP_DIR, environ=None):
    if not (app_dir / "release.json").is_file():
        return app_dir
    environ = os.environ if environ is None else environ
    local = Path(environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    return local / "NicholasNiceNeckerCubeExperiment"


def bundled_python(app_dir=APP_DIR):
    if (app_dir / "release.json").is_file():
        return app_dir.parent / "runtime" / "python.exe"
    return None


STATE_DIR = state_directory()
