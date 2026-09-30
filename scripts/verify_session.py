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
    parser.add_argument('--windowed', action='store_true')
    parser.add_argument('--fake-biosemi', action='store_true', help='Exercise normal mode with an injected fake serial port; never touches hardware.')
    parser.add_argument('--fail-write-at', type=int, default=0)
    args = parser.parse_args()
    if args.fail_write_at < 0 or (args.fail_write_at and not args.fake_biosemi):
        parser.error('--fail-write-at requires --fake-biosemi and a positive attempt number')
    app, folder = args.app.resolve(), args.output.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(app))
    from settings import default_settings
    from participant import HANDEDNESS_KEY
    config = default_settings()
    config.update(test_mode=not args.fake_biosemi, full_screen=True, monitor_width_cm=53., monitor_distance_cm=80.,
                  volume=0., practice_reps=1, baseline_blocks=1, baseline_reps=1,
                  conditioning_blocks=1, conditioning_reps=1, post_blocks=1, post_reps=1,
                  no_go_demo_reps=1, go_demo_reps=1, stimulus_seconds=.03, practice_seconds=.12,
                  necker_seconds=.95, response_seconds=.12, conditioning_seconds=.12,
                  gonogo_seconds=.12, fixation_seconds=.12, blank_min_frames=1,
                  blank_max_frames=2, tone_seconds=.03)
    if args.windowed:
        config.update(full_screen=False, window_width=800, window_height=600)
    participant = ({'participant_ID': '0000', 'age': 25, 'sex': 'Female',
                    HANDEDNESS_KEY: 'Right handed', 'colorblind': False,
                    'manual_removed_electrodes': []} if args.fake_biosemi else None)
    (folder / 'session.json').write_text(json.dumps({'settings': config, 'participant': participant,
        'safe_id': 'SYNTHETIC_SERIAL_CHECK' if args.fake_biosemi else 'TEST',
        'biosemi_recording_confirmed': args.fake_biosemi}))
    harness = '''import sys
from pathlib import Path
from types import SimpleNamespace
import json
sys.path.insert(0, sys.argv[1])
from psychopy.hardware import keyboard
import serial
def forbidden_serial(*args, **kwargs):
    raise AssertionError('Test mode tried to open serial hardware')
serial.Serial = forbidden_serial
probe = {'opens': 0, 'writes': [], 'closes': 0}
if sys.argv[2] == 'serial':
    class FakePort:
        def __init__(self, **kwargs):
            assert kwargs == dict(port='COM3', baudrate=115200, bytesize=8, parity='N', stopbits=1,
                                  timeout=0, write_timeout=0, rtscts=False, dsrdtr=False, xonxoff=False)
            probe['opens'] += 1
            assert probe['opens'] == 1, 'Serial was opened more than once'
        def write(self, value):
            assert isinstance(value, bytes) and len(value) == 1
            probe['writes'].append(value[0])
            return 0 if len(probe['writes']) == int(sys.argv[3]) else 1
        def close(self):
            probe['closes'] += 1
    serial.Serial = FakePort
original_keys = keyboard.Keyboard.getKeys
def simulated(self, keyList=None, **kwargs):
    if keyList == ['escape']:
        return original_keys(self, keyList=keyList, **kwargs)
    if keyList and self.clock.getTime() > .15:
        return [SimpleNamespace(name=keyList[0], rt=self.clock.getTime(), duration=None)]
    return []
keyboard.Keyboard.getKeys = simulated
from runtime import run_worker
try:
    status = run_worker(Path(__file__).parent / 'session.json')
finally:
    (Path(__file__).parent / 'serial_probe.json').write_text(json.dumps(probe))
raise SystemExit(status)
'''
    (folder / 'harness.py').write_text(harness, encoding='utf-8')
    env = dict(os.environ, APPDATA=str(folder / 'profile'), PYTHONDONTWRITEBYTECODE='1')
    with (folder / 'runner.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen([sys.executable, '-E', '-s', '-B', '-u',
                                    str(folder / 'harness.py'), str(app),
                                    'serial' if args.fake_biosemi else 'test', str(args.fail_write_at)],
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
    probe = json.loads((folder / 'serial_probe.json').read_text())
    with Path(result['trigger_log']).open(newline='') as stream:
        markers = list(csv.DictReader(stream))
    if args.fail_write_at:
        assert process.returncode == 1 and result['status'] == 'failed', result
        assert probe['opens'] == probe['closes'] == 1
        assert len(probe['writes']) == args.fail_write_at
        assert markers[-1]['status'] == 'error' and result['triggers']['error'] == 1
        assert Path(result['data_file']).is_file()
        print('Injected short-write test passed: session failed, partial data and trigger error saved, port closed.')
        return
    assert process.returncode == 0 and result['status'] == 'completed', result
    with Path(result['data_file']).open(encoding='utf-8-sig') as data:
        rows = list(csv.DictReader(data))
    expected = {'NeckerBaseline.started': 8, 'Necker.started': 16, 'trial.started': 6,
                'dontpress1.started': 3, 'pressEx.started': 1, 'Thanks.started': 1}
    assert {key: sum(bool(r.get(key)) for r in rows) for key in expected} == expected
    if args.fake_biosemi:
        assert probe == {'opens': 1, 'writes': [1, 2] + [1] * 8, 'closes': 1}, probe
        assert all(r['test_mode'] == 'False' and r['serial_enabled'] == 'True' for r in rows)
        assert all(r['status'] == 'sent' and r['backend'] == 'serial' for r in markers)
    else:
        assert probe == {'opens': 0, 'writes': [], 'closes': 0}, probe
        assert all(r['participant_ID'] == 'TEST' and r['test_mode'] == 'True' and
                   r['serial_enabled'] == 'False' and r['biosemi_recording_confirmed'] == 'False' for r in rows)
        assert all(r['status'] == 'skipped_disabled' and r['backend'] == 'null' for r in markers)
    assert [int(r['code']) for r in markers] == [1, 2] + [1] * 8
    print('Session passed: 30 trials, 4 demonstrations, saved results, correct trigger audit; '
          f'full_screen={config["full_screen"]}.')


if __name__ == '__main__':
    main()
