"""Validation at the GUI/runtime boundary, independent of Tk and hardware."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from participant import HANDEDNESS_KEY, ParticipantError, validate_participant
from settings import default_settings, load_settings, save_settings, validate_settings

VALID = {'participant_ID': '0012', 'age': '25', 'sex': 'Female',
         HANDEDNESS_KEY: 'Right handed', 'colorblind': False,
         'manual_removed_electrodes': 'ft7, P9; Oz, FT7'}


class ParticipantTests(unittest.TestCase):
    def test_normalization_preserves_leading_zeroes_and_bool_false(self):
        result = validate_participant(VALID)
        self.assertEqual(result['participant_ID'], '0012')
        self.assertEqual(result['age'], 25)
        self.assertIs(result['colorblind'], False)
        self.assertEqual(result['manual_removed_electrodes'], ['FT7', 'P9', 'OZ'])

    def test_invalid_values_identify_the_field(self):
        cases = {
            'participant_ID': ['', 'abc', '-1', '1.5', '²', '١٢', '../0012', 12],
            'age': ['', '1.5', 0, 121, -1, True, 25.0, '1e2', '²', '9' * 10000],
            'sex': ['', 'unknown', None],
            HANDEDNESS_KEY: ['', 'whatever', None],
            'colorblind': ['', None, 'No', 0, 1],
            'manual_removed_electrodes': [False, [1], 'FT7\x00'],
        }
        for key, invalids in cases.items():
            for value in invalids:
                with self.subTest(field=key, value=str(value)[:30]), self.assertRaises(ParticipantError) as error:
                    validate_participant({**VALID, key: value})
                self.assertEqual(error.exception.field, key)

    def test_age_boundaries_and_all_selection_values(self):
        for age in (1, 120):
            for sex in ('Female', 'Male'):
                for handedness in ('Right handed', 'Left handed', 'Ambidextrous'):
                    result = validate_participant({**VALID, 'age': age, 'sex': sex, HANDEDNESS_KEY: handedness,
                                                   'colorblind': True, 'manual_removed_electrodes': ''})
                    self.assertEqual(result['age'], age)
                    self.assertEqual(result['manual_removed_electrodes'], [])


class LaunchSettingsTests(unittest.TestCase):
    def test_existing_settings_keep_output_and_calibration_when_sophia_is_added(self):
        original = default_settings()
        original.pop('sophia_mode')
        original.update(output_dir='D:/2 - Results/Necker Cube/Necker Response Results',
                        monitor_width_cm=53.0, monitor_distance_cm=80.0)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'settings.json'
            path.write_text(json.dumps(original))
            loaded = load_settings(path)
            self.assertTrue(loaded.pop('sophia_mode'))
            self.assertEqual(loaded, original)
            loaded['sophia_mode'] = False
            save_settings(loaded, path)
            self.assertEqual(load_settings(path), loaded)

    def test_defaults_enable_sophia_and_lock_port(self):
        config = default_settings()
        self.assertTrue(config['sophia_mode'])
        for port in ('COM1', 'COM9', '/dev/ttyUSB0'):
            with self.subTest(port=port), self.assertRaisesRegex(ValueError, 'locked to COM3'):
                validate_settings({**config, 'serial_port': port})


if __name__ == '__main__':
    unittest.main()
