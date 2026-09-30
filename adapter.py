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
    from .triggers import SerialConnection
else:
    from settings import APP_DIR, default_settings, validate_settings
    from triggers import SerialConnection

REFERENCE = APP_DIR / "reference" / "experiment_source.py"
REFERENCE_SHA256 = "0a0ce03f9fc72d15bf38b5319e6b8819df9c16f708bca9c4df4aebcc3d504204"


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
    # Preserve the three original call sites; encode marker values as raw bytes
    # inside the checked transport, never via UTF-8 chr(...). No new markers.
    source = _replace(source, '\n    port.write(str.encode(chr(1)))',
                      '\n    send_trigger(1, label="initial_baseline")', 1)
    source = _replace(source, '\n    port.write(str.encode(chr(2)))',
                      '\n    send_trigger(2, label="initial_conditioned")', 1)
    source = _replace(source, '\n        port.write(str.encode(chr(1)))',
                      '\n        send_trigger(1, label="practice_start")', 1)
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
    source = _replace(source, '    # create some handy timers',
                      '    fit_presentation(win, locals())\n\n    # create some handy timers', 1)
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
    validate_trigger_sites(source)
    return source


def validate_trigger_sites(source):
    """Reject absent or displaced marker calls before opening hardware."""
    tree = ast.parse(source)
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    calls = sorted((n for n in ast.walk(run) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name) and n.func.id == 'send_trigger'),
                   key=lambda n: n.lineno)
    actual = [(ast.literal_eval(n.args[0]),
               ast.literal_eval(next(k.value for k in n.keywords if k.arg == 'label')))
              for n in calls]
    if actual != [(1, 'initial_baseline'), (2, 'initial_conditioned'), (1, 'practice_start')]:
        raise RuntimeError('Trigger integration mismatch: original marker schedule is missing or changed.')
    top_calls = [n.value for n in run.body if isinstance(n, ast.Expr)]
    practice = next(n for n in ast.walk(run) if isinstance(n, ast.For)
                    and isinstance(n.iter, ast.Name) and n.iter.id == 'trials_9')
    if calls[0] not in top_calls or calls[1] not in top_calls or calls[2] not in list(ast.walk(practice)):
        raise RuntimeError('Trigger integration mismatch: marker placement changed.')
    if any(isinstance(n, ast.Call) and ast.unparse(n.func) == 'port.write' for n in ast.walk(tree)):
        raise RuntimeError('Trigger integration mismatch: unchecked serial write.')
