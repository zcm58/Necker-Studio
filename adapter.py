"""Small, checked adaptations of the frozen Builder export.

The original frame loops are retained. Only explicitly exposed settings and
application IO are changed; no experiment code is generated from user input.
"""
from __future__ import annotations

import ast
import hashlib
import re

if __package__:
    from .settings import APP_DIR, default_settings, validate_settings
else:
    from settings import APP_DIR, default_settings, validate_settings

REFERENCE = APP_DIR / "reference" / "experiment_source.py"
REFERENCE_SHA256 = "0a0ce03f9fc72d15bf38b5319e6b8819df9c16f708bca9c4df4aebcc3d504204"


class SerialConnection:
    """Own one physical handle, including when Builder asks to open it twice."""

    def __init__(self, config, factory=None):
        self.config = config
        self.factory = factory
        self.handle = None

    def open(self):
        if self.handle is not None:
            return self.handle
        if not self.config["serial_enabled"]:
            self.handle = _NoSerial()
            return self.handle
        factory = self.factory
        if factory is None:
            import serial
            factory = serial.Serial
        try:
            self.handle = factory(port=self.config["serial_port"],
                                  baudrate=self.config["serial_baud"])
        except Exception as exc:
            raise RuntimeError(
                f"Could not open {self.config['serial_port']}: {exc}\n"
                "Close any other program using this port, select the correct port "
                "in File > Settings, or disable serial triggers for a practice run."
            ) from exc
        return self.handle

    def close(self):
        if self.handle is not None:
            handle, self.handle = self.handle, None
            handle.close()


class _NoSerial:
    def write(self, value):
        return len(value)

    def close(self):
        pass


def select_audio_backend(preference, available):
    """Accept both legacy ordered preference lists and newer single names."""
    preferences = preference if isinstance(preference, (list, tuple)) else [preference]
    names = {str(name).lower(): name for name in available}
    for value in preferences:
        if str(value).lower() in names:
            return names[str(value).lower()]
    raise RuntimeError(f"No installed sound backend matches the PsychoPy preference {preference!r}.")


def _replace(source, old, new, count=None):
    actual = source.count(old)
    if actual == 0 or (count is not None and actual != count):
        raise RuntimeError(f"Experiment integration mismatch: {old!r} ({actual} matches)")
    return source.replace(old, new)


def build_source(config):
    config = validate_settings(config)
    defaults = default_settings()
    raw = REFERENCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA256:
        raise RuntimeError("The bundled reference experiment has changed; restore it before running.")
    source = raw.decode("utf-8-sig").replace("\r\n", "\n")

    # Changes below are application plumbing, not experimental task logic.
    source = _replace(source, 'serial.Serial(port = "COM3" , baudrate = 115200)',
                      'open_serial()', 2)
    source = _replace(source, 'port.close();', 'close_serial();', 2)
    source = _replace(source, "= prefs.hardware['audioLib']", '= studio_audio_backend', 2)
    source = _replace(source, 'data.importConditions(', 'get_conditions(', 6)
    source = _replace(source, 'if defaultKeyboard.getKeys(keyList=["escape"]):',
                      'if check_abort(defaultKeyboard.getKeys(keyList=["escape"])):')
    source = _replace(source, "if defaultKeyboard.getKeys(keyList=['escape']):",
                      "if check_abort(defaultKeyboard.getKeys(keyList=['escape'])):", 1)
    # Preserve phase-end trigger locations, including the original initialization
    # writes; do not silently move them onto screen flips or enable disabled code.
    source = _replace(source, "monitor='testMonitor'", "monitor=studio_monitor", 1)
    source = _replace(source, "fullscr=_fullScr, screen=0",
                      f"fullscr=_fullScr, screen={config['screen'] - 1}", 1)
    source = _replace(source, "_fullScr = True", f"_fullScr = {config['full_screen']!r}", 1)
    source = _replace(source, "_winSize = [1920, 1080]",
                      f"_winSize = {[config['window_width'], config['window_height']]!r}", 1)
    # Absolute origin avoids the previous researcher's hard-coded OneDrive path.
    source = re.sub(r"originPath='[^'\n]*'", lambda m: f"originPath={str(REFERENCE)!r}", source)

    loops = {'trials_9': 'practice_reps', 'trials_6': 'baseline_blocks',
             'trials_3': 'baseline_reps', 'trials_5': 'conditioning_blocks',
             'trials': 'conditioning_reps', 'trials_4': 'post_blocks',
             'trials_2': 'post_reps', 'trials_7': 'no_go_demo_reps',
             'trials_8': 'go_demo_reps'}
    for loop, key in loops.items():
        if config[key] != defaults[key]:
            pattern = rf"({loop} = data\.TrialHandler2\(\s*\n\s*name='{loop}',\s*\n\s*nReps=)[\d.]+"
            source, count = re.subn(pattern, lambda m: m[1] + repr(float(config[key])), source)
            if count != 1:
                raise RuntimeError(f"Missing repetition setting for {loop}")

    # Apply routine-wide timer changes first so equal custom values cannot
    # accidentally match a later replacement. Each edit sees original tokens.
    routine_keys = {'NeckerBaseline': ('practice_seconds', .8),
                    'Necker': ('necker_seconds', 1.5),
                    'blank': ('response_seconds', 3.0),
                    'trial': ('conditioning_seconds', 1.5),
                    'goNogo': ('gonogo_seconds', 1.4),
                    'cross': ('fixation_seconds', 1.0)}
    starts = list(re.finditer(r'# --- Prepare to start Routine "([^"]+)" ---', source))
    for index in range(len(starts) - 1, -1, -1):
        match = starts[index]
        name = match[1]
        end = starts[index + 1].start() if index + 1 < len(starts) else len(source)
        section = source[match.start():end]
        changes = {}
        if name in routine_keys:
            key, old = routine_keys[name]
            if config[key] != defaults[key]:
                changes[old] = float(config[key])
        if name in ('NeckerBaseline', 'Necker', 'trial') and config['stimulus_seconds'] != .15:
            changes[.15] = float(config['stimulus_seconds'])
        if config['tone_seconds'] != .05 and name in ('Necker', 'trial', 'Instr_gonogo', 'dontpress1', 'pressEx'):
            changes[.05] = float(config['tone_seconds'])
        if changes:
            pattern = re.compile(r'(tStartRefresh\s*\+\s*|routineTimer\.getTime\(\)\s*<\s*|routineTimer\.addTime\(-)(\d+(?:\.\d*)?|\.\d+)')
            section = pattern.sub(lambda m: m[1] + repr(changes[float(m[2])])
                                  if float(m[2]) in changes else m[0], section)
            source = source[:match.start()] + section + source[end:]
    if config['tone_seconds'] != .05:
        source = _replace(source, 'secs=0.05', f"secs={float(config['tone_seconds'])!r}")
    if config['volume'] != 1:
        source = _replace(source, '.setVolume(1.0', f".setVolume({float(config['volume'])!r}")
    if (config['blank_min_frames'], config['blank_max_frames']) != (62, 125):
        source = _replace(source, 'randint(62, 125)',
                          f"randint({config['blank_min_frames']}, {config['blank_max_frames']})", 4)
    if (config['cube_width_deg'], config['cube_height_deg']) != (6, 5.25):
        source = _replace(source, 'size=(6, 5.25)',
                          f"size=({config['cube_width_deg']!r}, {config['cube_height_deg']!r})", 4)
    ast.parse(source)
    return source
