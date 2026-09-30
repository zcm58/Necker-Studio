"""Run PsychoPy in a separate process so the operator interface stays responsive."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

if __package__:
    from .app_paths import STATE_DIR, bundled_python
    from .triggers import require_trigger_output
    from .settings import APP_DIR, condition_rows, validate_settings, serial_triggers_enabled
    from .participant import session_participant, require_recording_confirmation
else:
    from app_paths import STATE_DIR, bundled_python
    from triggers import require_trigger_output
    from settings import APP_DIR, condition_rows, validate_settings, serial_triggers_enabled
    from participant import session_participant, require_recording_confirmation


def output_directory(config):
    path = Path(config['output_dir']).expanduser()
    path = path.resolve() if path.is_absolute() else (STATE_DIR / path).resolve()
    return path / 'test_runs' if config['test_mode'] else path


def discover_python(config):
    """Use the chosen engine, current environment, or an installed standalone runtime."""
    selected = config.get('psychopy_python', '').strip()
    if selected:
        selected_path = Path(selected).expanduser()
        candidates = [selected_path if selected_path.is_absolute() else APP_DIR / selected_path]
    elif bundled_python(APP_DIR) is not None:
        candidates = [bundled_python(APP_DIR)]
    else:
        candidates = [APP_DIR / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'), Path(sys.executable)]
        local = os.environ.get('LOCALAPPDATA')
        if local:
            candidates += [Path(local) / 'Programs' / name / 'python.exe'
                           for name in ('PsychoPy', 'PsychoPy3')]
        for env in ('ProgramFiles', 'ProgramFiles(x86)'):
            if os.environ.get(env):
                candidates += [Path(os.environ[env]) / name / 'python.exe'
                               for name in ('PsychoPy', 'PsychoPy3')]
    probe = "import importlib.util; assert importlib.util.find_spec('psychopy'), 'PsychoPy is not installed'"
    for path in dict.fromkeys(candidates):
        if not path.is_file():
            continue
        try:
            result = subprocess.run([str(path), '-E', '-s', '-c', probe], capture_output=True,
                                    timeout=15, creationflags=_no_window())
            if result.returncode == 0:
                return str(path)
        except (OSError, subprocess.TimeoutExpired):
            continue
    raise RuntimeError(
        "A Python interpreter with PsychoPy could not be found. In File > Settings, "
        "select the python.exe inside your PsychoPy installation, or run main.py "
        "with a PyCharm interpreter that already has PsychoPy installed."
    )


def _no_window():
    return subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


@dataclass
class SessionHandle:
    process: subprocess.Popen
    session_dir: Path
    log_path: Path
    result_path: Path
    stop_path: Path

    def poll(self):
        return self.process.poll()

    def request_stop(self):
        self.stop_path.touch()


def start_session(config, participant=None, *, recording_confirmed=False):
    config = validate_settings(config)
    require_trigger_output(config)
    info = session_participant(config, participant)
    if config['test_mode']:
        recording_confirmed = False
    require_recording_confirmation(config, recording_confirmed)
    engine = discover_python(config)
    # Preserve the actual ID in metadata while preventing path traversal and
    # Windows reserved filenames in the output path.
    safe_id = re.sub(r'[^\w.-]+', '_', info['participant_ID'], flags=re.UNICODE).strip(' ._')[:80]
    safe_id = safe_id or 'anonymous'
    stamp = datetime.now().strftime('%Y-%m-%d_%H%M%S_%f')
    base = output_directory(config)
    base.mkdir(parents=True, exist_ok=True)
    session_dir = base / f'session_{safe_id}_{stamp}'
    session_dir.mkdir(exist_ok=False)
    payload = {'settings': config, 'participant': info, 'safe_id': safe_id,
               'biosemi_recording_confirmed': recording_confirmed is True,
               'engine': engine, 'created': datetime.now().astimezone().isoformat()}
    request_path = session_dir / 'session.json'
    request_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    log_path = session_dir / 'runner.log'
    result_path = session_dir / 'result.json'
    stop_path = session_dir / 'stop.request'
    try:
        with log_path.open('w', encoding='utf-8') as log:
            process = subprocess.Popen(
                [engine, '-E', '-s', '-u', str(Path(__file__).resolve()), '--session', str(request_path)],
                cwd=str(APP_DIR), stdout=log, stderr=subprocess.STDOUT,
                creationflags=_no_window(),
            )
    except OSError as exc:
        result_path.write_text(json.dumps({'status': 'failed', 'error': str(exc)}, indent=2), encoding='utf-8')
        raise
    return SessionHandle(process, session_dir, log_path, result_path, stop_path)


def _monitor(config):
    from psychopy import monitors
    monitor = monitors.Monitor(config['monitor_name'])
    width = config.get('monitor_width_cm', '')
    distance = config.get('monitor_distance_cm', '')
    if width != '':
        monitor.setWidth(float(width))
    if distance != '':
        monitor.setDistance(float(distance))
    if width != '' or distance != '':
        monitor.setSizePix([config['window_width'], config['window_height']])
    if not monitor.getWidth() or not monitor.getDistance() or not monitor.getSizePix():
        raise RuntimeError(
            f"Monitor '{config['monitor_name']}' has no complete calibration. "
            "The experiment uses visual degrees. In File > Settings enter the measured "
            "screen width (cm), viewing distance (cm), and the display's pixel dimensions, "
            "or choose an existing calibrated PsychoPy monitor profile."
        )
    return monitor


def run_worker(request_path):
    request_path = Path(request_path).resolve()
    session_dir = request_path.parent
    result_path = session_dir / 'result.json'
    stop_path = session_dir / 'stop.request'
    result = {'status': 'failed'}
    experiment = window = connection = namespace = None
    aborted = False
    saved = False
    last_stop_check = 0.0
    cleanup_errors = []
    try:
        payload = json.loads(request_path.read_text(encoding='utf-8'))
        config = validate_settings(payload['settings'])
        require_trigger_output(config)
        payload['participant'] = session_participant(config, payload.get('participant'))
        if config['test_mode']:
            payload['biosemi_recording_confirmed'] = False
        require_recording_confirmation(config, payload.get('biosemi_recording_confirmed', False))
        from adapter import SerialConnection, build_source, select_audio_backend
        from presentation import fit_presentation
        # Build before importing the engine; malformed settings cannot partially
        # initialize acquisition hardware.
        source = build_source(config)
        import psychopy
        from psychopy import logging, sound, prefs
        backend = select_audio_backend(prefs.hardware['audioLib'], sound.Sound.getBackends())
        monitor = _monitor(config)
        connection = SerialConnection(config)
        connection.open()

        def check_abort(keys):
            nonlocal aborted, last_stop_check
            if keys:
                aborted = True
            now = time.monotonic()
            if now - last_stop_check >= .05:
                last_stop_check = now
                aborted = aborted or stop_path.exists()
            return aborted

        namespace = {
            '__name__': 'necker_experiment',
            '__file__': str(APP_DIR / 'assets' / 'experiment.py'),
            'open_serial': connection.open,
            'close_serial': connection.close,
            'send_trigger': connection.send,
            'get_conditions': lambda filename, selection=None: condition_rows(config, filename, selection),
            'check_abort': check_abort,
            'studio_monitor': monitor,
            'studio_audio_backend': backend,
            'fit_presentation': fit_presentation,
        }
        # No shell or user supplied Python is evaluated: this is the hash-checked
        # bundled Builder export with validated literal settings.
        exec(compile(source, str(APP_DIR / 'reference' / 'experiment_source.py'), 'exec'), namespace)
        namespace['psychopyVersion'] = psychopy.__version__
        info = dict(namespace['expInfo'])
        info.update(payload['participant'])
        info['biosemi_recording_confirmed'] = payload.get('biosemi_recording_confirmed', False)
        info['test_mode'] = config['test_mode']
        info['psychopyVersion|hid'] = psychopy.__version__
        # setupData uses the ID in its filename. Substitute only during filename
        # construction, then restore the exact participant text in saved metadata.
        original_id = info['participant_ID']
        info['participant_ID'] = payload['safe_id']
        (session_dir / 'data').mkdir(exist_ok=True)
        experiment = namespace['setupData'](info, dataDir=str(session_dir))
        info['participant_ID'] = original_id
        experiment.extraInfo['participant_ID'] = original_id
        info['studio_settings'] = str(request_path)
        info['serial_enabled'] = serial_triggers_enabled(config)
        info['monitor_width_cm'] = monitor.getWidth()
        info['monitor_distance_cm'] = monitor.getDistance()
        info['monitor_size_pixels'] = monitor.getSizePix()
        namespace['setupLogging'](experiment.dataFileName)
        result['data_file'] = experiment.dataFileName + '.csv'
        result['psychopy_version'] = psychopy.__version__
        if not check_abort([]):
            window = namespace['setupWindow'](expInfo=info)
            namespace['setupDevices'](expInfo=info, thisExp=experiment, win=window)
            if not check_abort([]):
                namespace['run'](expInfo=info, thisExp=experiment, win=window, globalClock='float')
        if not aborted:
            connection.validate_completion(len(config['conditions']['LorR.xlsx']) * config['practice_reps'])
        namespace['saveData'](experiment)
        saved = True
        result['status'] = 'aborted' if aborted else 'completed'
    except BaseException as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
        traceback.print_exc()
    finally:
        # Always preserve whatever the handler collected before a failure/abort.
        if experiment is not None and namespace is not None:
            if not saved:
                try:
                    namespace['saveData'](experiment)
                    saved = True
                except Exception as exc:
                    cleanup_errors.append(f'Data save failed: {exc}')
            if saved:
                try:
                    experiment.abort()  # prevent duplicate auto-save at exit
                except Exception as exc:
                    cleanup_errors.append(f'Data handler cleanup: {exc}')
        if connection is not None:
            result['triggers'] = connection.summary()
            try:
                trigger_log = session_dir / 'trigger_log.csv'
                connection.export(trigger_log)
                result['trigger_log'] = str(trigger_log)
            except Exception as exc:
                cleanup_errors.append(f'Trigger log save failed: {exc}')
            try:
                connection.close()
            except Exception as exc:
                cleanup_errors.append(f'Serial cleanup: {exc}')
        if namespace is not None:
            try:
                manager = namespace.get('deviceManager')
                server = getattr(manager, 'ioServer', None)
                if server is not None:
                    server.quit()
            except Exception as exc:
                cleanup_errors.append(f'Keyboard cleanup: {exc}')
        if window is not None:
            try:
                window.close()
            except Exception as exc:
                cleanup_errors.append(f'Window cleanup: {exc}')
        if 'psychopy.logging' in sys.modules:
            try:
                sys.modules['psychopy.logging'].flush()
            except Exception as exc:
                cleanup_errors.append(f'Log flush: {exc}')
        if cleanup_errors:
            result['cleanup_errors'] = cleanup_errors
            if result['status'] == 'completed':
                result['status'] = 'failed'
                result['error'] = '; '.join(cleanup_errors)
        result['finished'] = datetime.now().astimezone().isoformat()
        temporary = result_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        temporary.replace(result_path)
    return 1 if result['status'] == 'failed' else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(run_worker(args.session))
