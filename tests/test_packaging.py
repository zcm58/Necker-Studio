"""Installed state and interpreter selection must not depend on the build machine."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app_paths import state_directory, bundled_python
import runtime
from settings import default_settings


class InstalledPathsTests(unittest.TestCase):
    def test_development_keeps_existing_project_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            app = Path(temporary)
            self.assertEqual(state_directory(app), app)
            self.assertIsNone(bundled_python(app))

    def test_installed_state_survives_a_different_install_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for version in ('v1', 'v2'):
                app = root / version / 'app'
                app.mkdir(parents=True)
                (app / 'release.json').write_text('{}')
                state = state_directory(app, {'LOCALAPPDATA': str(root / 'user')})
                self.assertEqual(state, root / 'user' / 'NicholasNiceNeckerCubeExperiment')
                self.assertEqual(bundled_python(app), app.parent / 'runtime' / 'python.exe')

    def test_packaged_engine_is_preferred_and_missing_engine_is_not_silently_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            app = Path(temporary) / 'app'
            app.mkdir()
            (app / 'release.json').write_text('{}')
            engine = bundled_python(app)
            with patch.object(runtime, 'APP_DIR', app), patch.object(runtime.subprocess, 'run', return_value=Mock(returncode=0)) as probe:
                with self.assertRaises(RuntimeError):
                    runtime.discover_python(default_settings())
                probe.assert_not_called()
                engine.parent.mkdir()
                engine.touch()
                self.assertEqual(runtime.discover_python(default_settings()), str(engine))

    def test_relative_output_uses_writable_state_and_absolute_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            config = default_settings()
            with patch.object(runtime, 'STATE_DIR', root / 'state'):
                self.assertEqual(runtime.output_directory(config), root / 'state' / 'data')
                config['test_mode'] = True
                self.assertEqual(runtime.output_directory(config), root / 'state' / 'data' / 'test_runs')
                config['output_dir'] = str(root / 'chosen')
                self.assertEqual(runtime.output_directory(config), root / 'chosen' / 'test_runs')


if __name__ == '__main__':
    unittest.main()
