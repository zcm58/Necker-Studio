"""Exercise real worker cleanup and exports with fake PsychoPy and serial IO."""
import csv
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runtime
from settings import default_settings
from participant import HANDEDNESS_KEY
from test_triggers import Port

PARTICIPANT = {'participant_ID': '0012', 'age': 25, 'sex': 'Female',
               HANDEDNESS_KEY: 'Right handed', 'colorblind': False,
               'manual_removed_electrodes': []}

STUB_SOURCE = '''
from pathlib import Path
from types import SimpleNamespace
expInfo = {}
deviceManager = SimpleNamespace(ioServer=None)
def setupData(info, dataDir):
    return SimpleNamespace(extraInfo=info, dataFileName=str(Path(dataDir)/'data'/'fake'), abort=lambda:None)
def setupLogging(filename): pass
def setupWindow(expInfo): return SimpleNamespace(close=lambda:None)
def setupDevices(**kwargs): pass
def saveData(experiment): Path(experiment.dataFileName + '.saved').touch()
def run(**kwargs):
    send_trigger(1, label='initial_baseline')
    send_trigger(2, label='initial_conditioned')
    for index in range(8):
        send_trigger(1, label='practice_start')
'''


class WorkerTriggerTests(unittest.TestCase):
    def worker(self, *, source=STUB_SOURCE, config=None, port=None, open_error=None, stop=False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        config = config or default_settings()
        request = folder / 'session.json'
        request.write_text(json.dumps({'settings': config, 'participant': PARTICIPANT,
                                      'safe_id': '0012', 'biosemi_recording_confirmed': True}))
        if stop:
            (folder / 'stop.request').touch()
        port = port or Port()
        serial = ModuleType('serial')
        serial.Serial = Mock(return_value=port, side_effect=open_error)
        psychopy = ModuleType('psychopy')
        psychopy.__version__ = 'test'
        psychopy.logging = SimpleNamespace(flush=lambda: None)
        psychopy.prefs = SimpleNamespace(hardware={'audioLib': 'ptb'})
        psychopy.sound = SimpleNamespace(Sound=SimpleNamespace(getBackends=lambda: {'ptb': object()}))
        monitor = SimpleNamespace(getWidth=lambda:53, getDistance=lambda:80,
                                  getSizePix=lambda:[1920, 1080])
        with patch.dict(sys.modules, {'serial': serial, 'psychopy': psychopy}), \
             patch('adapter.build_source', return_value=source), \
             patch.object(runtime, '_monitor', return_value=monitor), patch('traceback.print_exc'):
            code = runtime.run_worker(request)
        result = json.loads((folder / 'result.json').read_text())
        rows = []
        if 'trigger_log' in result:
            with Path(result['trigger_log']).open(newline='') as stream:
                rows = list(csv.DictReader(stream))
        return code, result, rows, port, serial.Serial, folder

    def test_enabled_worker_sends_original_schedule_and_exports_success_only_after_write(self):
        code, result, rows, port, factory, folder = self.worker()
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(port.writes, [b'\x01', b'\x02'] + [b'\x01'] * 8)
        factory.assert_called_once()
        self.assertEqual(port.close_calls, 1)
        self.assertEqual(result['triggers']['sent'], 10)
        self.assertTrue(all(r['status'] == 'sent' and r['backend'] == 'serial' for r in rows))
        self.assertTrue((folder / 'data/fake.saved').is_file())

    def test_failed_or_short_write_aborts_saves_partial_data_logs_error_and_closes(self):
        for port in (Port(returned=0), Port(error=OSError('device disconnected'))):
            with self.subTest(port=port):
                code, result, rows, port, factory, folder = self.worker(port=port)
                self.assertEqual(code, 1)
                self.assertEqual(result['status'], 'failed')
                self.assertIn('trigger code 1', result['error'])
                self.assertEqual(port.writes, [b'\x01'])
                self.assertEqual(port.close_calls, 1)
                self.assertEqual([r['status'] for r in rows], ['error'])
                self.assertTrue((folder / 'data/fake.saved').is_file())

    def test_missing_marker_callback_cannot_report_completed(self):
        for source in (STUB_SOURCE.replace("send_trigger(2, label='initial_conditioned')", 'pass'),
                       STUB_SOURCE[:STUB_SOURCE.index('def run(')] + 'def run(**kwargs): pass\n'):
            code, result, _, port, _, folder = self.worker(source=source)
            self.assertEqual(code, 1)
            self.assertEqual(result['status'], 'failed')
            self.assertIn('audit failed', result['error'])
            self.assertEqual(port.close_calls, 1)
            self.assertTrue((folder / 'data/fake.saved').is_file())

    def test_serial_open_failure_is_failed_not_null_and_no_presentation_runs(self):
        code, result, rows, port, factory, folder = self.worker(open_error=OSError('busy'))
        self.assertEqual(code, 1)
        self.assertIn('COM3', result['error'])
        self.assertEqual(result['triggers']['backend'], 'serial')
        self.assertEqual(rows, [])
        self.assertFalse((folder / 'data').exists())
        factory.assert_called_once()

    def test_test_mode_has_skipped_records_and_no_serial_open(self):
        code, result, rows, port, factory, _ = self.worker(config={**default_settings(), 'test_mode': True})
        self.assertEqual(code, 0)
        factory.assert_not_called()
        self.assertEqual(result['triggers']['backend'], 'null')
        self.assertEqual(result['triggers']['sent'], 0)
        self.assertEqual(result['triggers']['skipped_disabled'], 10)
        self.assertTrue(all(r['status'] == 'skipped_disabled' for r in rows))

    def test_normal_disabled_worker_and_launcher_fail_before_engine_or_hardware(self):
        config = {**default_settings(), 'serial_enabled': False}
        code, result, _, _, factory, _ = self.worker(config=config)
        self.assertEqual(code, 1)
        self.assertIn('required for normal runs', result['error'])
        factory.assert_not_called()
        with patch.object(runtime, 'discover_python') as engine:
            with self.assertRaisesRegex(ValueError, 'required for normal runs'):
                runtime.start_session(config, PARTICIPANT, recording_confirmed=True)
            engine.assert_not_called()

    def test_operator_abort_keeps_partial_audit_without_falsely_requiring_full_schedule(self):
        code, result, rows, port, _, _ = self.worker(stop=True)
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'aborted')
        self.assertEqual(rows, [])
        self.assertEqual(port.close_calls, 1)

    def test_cleanup_failure_does_not_report_success(self):
        port = Port()
        port.close = Mock(side_effect=OSError('close failed'))
        code, result, rows, _, _, _ = self.worker(port=port)
        self.assertEqual(code, 1)
        self.assertEqual(result['status'], 'failed')
        self.assertIn('Serial cleanup', result['error'])
        self.assertEqual(len(rows), 10)
