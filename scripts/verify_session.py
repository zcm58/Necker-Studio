"""Opt-in full-screen integration run with simulated responses and no hardware.

Use --app to test an installed app with its bundled Python. This uses shortened
trial settings and is a functional check, not a scientific timing measurement.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    app, folder = args.app.resolve(), args.output.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(app))
    from settings import default_settings
    config = default_settings()
    config.update(test_mode=True, full_screen=True, monitor_width_cm=53., monitor_distance_cm=80.,
                  volume=0., practice_reps=1, baseline_blocks=1, baseline_reps=1,
                  conditioning_blocks=1, conditioning_reps=1, post_blocks=1, post_reps=1,
                  no_go_demo_reps=1, go_demo_reps=1, stimulus_seconds=.03, practice_seconds=.12,
                  necker_seconds=.95, response_seconds=.12, conditioning_seconds=.12,
                  gonogo_seconds=.12, fixation_seconds=.12, blank_min_frames=1,
                  blank_max_frames=2, tone_seconds=.03)
    (folder / 'session.json').write_text(json.dumps({'settings': config, 'participant': None,
                                                  'safe_id': 'TEST', 'biosemi_recording_confirmed': False}))
    harness = '''import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, sys.argv[1])
from psychopy.hardware import keyboard
import serial
def forbidden_serial(*args, **kwargs):
    raise AssertionError('Test mode tried to open serial hardware')
serial.Serial = forbidden_serial
original_keys = keyboard.Keyboard.getKeys
def simulated(self, keyList=None, **kwargs):
    if keyList == ['escape']:
        return original_keys(self, keyList=keyList, **kwargs)
    if keyList and self.clock.getTime() > .15:
        return [SimpleNamespace(name=keyList[0], rt=self.clock.getTime(), duration=None)]
    return []
keyboard.Keyboard.getKeys = simulated
from runtime import run_worker
raise SystemExit(run_worker(Path(__file__).parent / 'session.json'))
'''
    (folder / 'harness.py').write_text(harness, encoding='utf-8')
    env = dict(os.environ, APPDATA=str(folder / 'profile'), PYTHONDONTWRITEBYTECODE='1')
    with (folder / 'runner.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen([sys.executable, '-E', '-s', '-B', '-u',
                                    str(folder / 'harness.py'), str(app)],
                                   cwd=app, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            process.wait(timeout=120)
        except subprocess.TimeoutExpired:
            (folder / 'stop.request').touch()
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=10)
            raise SystemExit('Functional session exceeded its limit; see runner.log.')
    result = json.loads((folder / 'result.json').read_text())
    assert process.returncode == 0 and result['status'] == 'completed', result
    with Path(result['data_file']).open(encoding='utf-8-sig') as data:
        rows = list(csv.DictReader(data))
    expected = {'NeckerBaseline.started': 8, 'Necker.started': 16, 'trial.started': 6,
                'dontpress1.started': 3, 'pressEx.started': 1, 'Thanks.started': 1}
    assert {key: sum(bool(r.get(key)) for r in rows) for key in expected} == expected
    assert all(r['participant_ID'] == 'TEST' and r['test_mode'] == 'True' and
               r['serial_enabled'] == 'False' and r['biosemi_recording_confirmed'] == 'False' for r in rows)
    print('Full-screen session passed: 30 trials, 4 demonstrations, saved results, no serial access.')


if __name__ == '__main__':
    main()
