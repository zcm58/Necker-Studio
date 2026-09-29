"""Runtime integration boundaries, without opening windows or hardware."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapter import select_audio_backend
import runtime
from settings import default_settings


class RuntimeTests(unittest.TestCase):
    def test_audio_legacy_lists_and_new_string_preferences(self):
        installed = {'ptb': object(), 'pygame': object()}
        self.assertEqual(select_audio_backend(['PTB', 'pygame'], installed), 'ptb')
        self.assertEqual(select_audio_backend('ptb', installed), 'ptb')
        self.assertEqual(select_audio_backend(['missing', 'pygame'], installed), 'pygame')
        with self.assertRaisesRegex(RuntimeError, 'sound backend'):
            select_audio_backend(['missing'], installed)

    def test_sessions_are_unique_and_participant_text_cannot_escape_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = default_settings()
            config['output_dir'] = temporary
            process = Mock()
            process.poll.return_value = None
            with patch.object(runtime, 'discover_python', return_value=sys.executable), \
                 patch.object(runtime.subprocess, 'Popen', return_value=process) as popen:
                participant = {'participant_ID': '../../CON:*?\\subject'}
                first = runtime.start_session(config, participant)
                second = runtime.start_session(config, participant)
                self.assertNotEqual(first.session_dir, second.session_dir)
                self.assertEqual(first.session_dir.parent, Path(temporary).resolve())
                payload = json.loads((first.session_dir / 'session.json').read_text())
                self.assertEqual(payload['participant']['participant_ID'], participant['participant_ID'])
                self.assertNotIn('/', payload['safe_id'])
                self.assertNotIn('\\', payload['safe_id'])
                first.request_stop()
                self.assertTrue(first.stop_path.exists())
                self.assertIsNone(first.poll())
                self.assertNotIn('shell', popen.call_args.kwargs)


    def test_project_environment_is_preferred_over_the_launching_interpreter(self):
        config = default_settings()
        with tempfile.TemporaryDirectory() as temporary:
            app = Path(temporary)
            engine = app / '.venv' / ('Scripts/python.exe' if runtime.os.name == 'nt' else 'bin/python')
            engine.parent.mkdir(parents=True)
            engine.touch()
            with patch.object(runtime, 'APP_DIR', app), \
                 patch.object(runtime.subprocess, 'run', return_value=Mock(returncode=0)) as probe:
                self.assertEqual(Path(runtime.discover_python(config)), engine)
                self.assertEqual(Path(probe.call_args.args[0][0]), engine)

    def test_relative_engine_path_uses_app_directory(self):
        config = default_settings()
        with tempfile.TemporaryDirectory() as temporary:
            app = Path(temporary)
            engine = app / 'engine' / 'python.exe'
            engine.parent.mkdir()
            engine.touch()
            config['psychopy_python'] = 'engine/python.exe'
            with patch.object(runtime, 'APP_DIR', app), \
                 patch.object(runtime.subprocess, 'run', return_value=Mock(returncode=0)):
                self.assertEqual(Path(runtime.discover_python(config)), engine)

    def test_worker_reports_bad_session_without_opening_psychopy(self):
        with tempfile.TemporaryDirectory() as temporary:
            session = Path(temporary) / 'session.json'
            session.write_text('{"settings": {}}')
            with patch('traceback.print_exc'):
                self.assertEqual(runtime.run_worker(session), 1)
            result = json.loads((session.parent / 'result.json').read_text())
            self.assertEqual(result['status'], 'failed')
            self.assertIn('missing', result['error'])


if __name__ == '__main__':
    unittest.main()
