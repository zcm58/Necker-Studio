"""Settings integrity checks; no PsychoPy, display, or hardware required."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

import settings


class SettingsValidationTests(unittest.TestCase):
    def setUp(self):
        self.config = settings.default_settings()

    def test_default_factory_and_validation_return_independent_condition_rows(self):
        reference = deepcopy(self.config)
        validated = settings.validate_settings(self.config)
        validated["conditions"]["LorR.xlsx"][0]["delay"] = 0.123
        validated["conditions"]["SoundA.xlsx"].pop()
        self.assertEqual(self.config, reference)
        self.assertEqual(settings.default_settings(), reference)

    def test_condition_subsets_do_not_modify_the_session(self):
        reference = deepcopy(self.config)
        for selection, count in ((None, 4), ("0:3", 3), ("3", 1)):
            with self.subTest(selection=selection):
                rows = settings.condition_rows(self.config, "SoundEx.xlsx", selection)
                self.assertEqual(len(rows), count)
                rows[0]["Sound"] = "changed.wav"
                rows.clear()
                self.assertEqual(self.config, reference)
        with self.assertRaisesRegex(ValueError, "Unsupported condition selection"):
            settings.condition_rows(self.config, "SoundEx.xlsx", "__import__('os')")

    def test_numeric_fields_reject_bool_strings_and_nonfinite_values(self):
        for key, values in (
            ("practice_reps", (True, False, "1", 1.5)),
            ("volume", (True, "0.5", float("nan"), float("inf"), -float("inf"))),
            ("full_screen", (1, 0, "true")),
        ):
            for value in values:
                with self.subTest(key=key, value=value):
                    config = deepcopy(self.config)
                    config[key] = value
                    with self.assertRaises(ValueError):
                        settings.validate_settings(config)

    def test_condition_numbers_are_finite_and_report_the_row(self):
        for column in ("delay", "ISI"):
            for value in (True, "0.2", float("nan"), float("inf"), -0.1):
                with self.subTest(column=column, value=value):
                    config = deepcopy(self.config)
                    config["conditions"]["LorR.xlsx"][2][column] = value
                    with self.assertRaisesRegex(ValueError, rf"LorR.xlsx, row 3, {column}"):
                        settings.validate_settings(config)

    def test_blank_metadata_and_literal_none_keep_distinct_types(self):
        self.config["conditions"]["LorR.xlsx"][0]["ISI"] = ""
        validated = settings.validate_settings(self.config)
        self.assertIsNone(validated["conditions"]["LorR.xlsx"][0]["ISI"])
        self.assertEqual(validated["conditions"]["SoundA.xlsx"][0]["GoNoGo"], "None")
        self.assertEqual(self.config["conditions"]["LorR.xlsx"][0]["ISI"], "")
        self.config["conditions"]["SoundA.xlsx"][0]["GoNoGo"] = None
        with self.assertRaisesRegex(ValueError, "GoNoGo must be text"):
            settings.validate_settings(self.config)

    def test_calibration_is_optional_paired_and_normalized_without_mutation(self):
        validated = settings.validate_settings(self.config)
        self.assertEqual(validated["monitor_width_cm"], "")
        self.assertEqual(validated["monitor_distance_cm"], "")
        self.config["monitor_width_cm"] = " 53.1 "
        self.config["monitor_distance_cm"] = "60"
        validated = settings.validate_settings(self.config)
        self.assertEqual(validated["monitor_width_cm"], 53.1)
        self.assertEqual(validated["monitor_distance_cm"], 60.0)
        self.assertEqual(self.config["monitor_width_cm"], " 53.1 ")
        self.config["monitor_distance_cm"] = ""
        with self.assertRaisesRegex(ValueError, "both monitor width and viewing distance"):
            settings.validate_settings(self.config)

    def test_invalid_calibration_is_rejected(self):
        for value in (True, 0, -10, "nan", "inf", "unknown"):
            with self.subTest(value=value):
                config = deepcopy(self.config)
                config["monitor_width_cm"] = value
                config["monitor_distance_cm"] = "60"
                with self.assertRaises(ValueError):
                    settings.validate_settings(config)

    def test_required_text_cannot_be_blank_but_engine_can_be_automatic(self):
        self.assertEqual(settings.validate_settings(self.config)["psychopy_python"], "")
        for key in ("output_dir", "monitor_name", "serial_port"):
            with self.subTest(key=key):
                config = deepcopy(self.config)
                config[key] = "  "
                with self.assertRaisesRegex(ValueError, "cannot be empty"):
                    settings.validate_settings(config)

    def test_schema_columns_and_demo_size_cannot_drift(self):
        invalid = []
        config = deepcopy(self.config)
        config["schema_version"] = True
        invalid.append(config)
        config = deepcopy(self.config)
        config["unknown_setting"] = 1
        invalid.append(config)
        config = deepcopy(self.config)
        del config["conditions"]["LorR.xlsx"][0]["image"]
        invalid.append(config)
        config = deepcopy(self.config)
        config["conditions"]["SoundEx.xlsx"].pop()
        invalid.append(config)
        config = deepcopy(self.config)
        config["conditions"]["SoundA.xlsx"].clear()
        invalid.append(config)
        for index, config in enumerate(invalid):
            with self.subTest(case=index), self.assertRaises(ValueError):
                settings.validate_settings(config)

    def test_exclusive_blank_frame_bounds_are_enforced(self):
        for minimum, maximum in ((125, 125), (126, 125)):
            with self.subTest(minimum=minimum, maximum=maximum):
                self.config["blank_min_frames"] = minimum
                self.config["blank_max_frames"] = maximum
                with self.assertRaisesRegex(ValueError, "upper bound must be greater"):
                    settings.validate_settings(self.config)

    def test_routines_cannot_clip_cube_exposure(self):
        for key in ("practice_seconds", "conditioning_seconds", "necker_seconds"):
            with self.subTest(key=key):
                config = deepcopy(self.config)
                config[key] = config["stimulus_seconds"] / 2
                with self.assertRaisesRegex(ValueError, "at least as long as the cube exposure"):
                    settings.validate_settings(config)

    def test_conditioning_routine_cannot_clip_the_tone(self):
        self.config["tone_seconds"] = 0.4
        self.config["conditioning_seconds"] = 0.3
        with self.assertRaisesRegex(ValueError, "at least as long as its tone"):
            settings.validate_settings(self.config)

    def test_main_routine_fits_the_latest_condition_tone(self):
        self.config["conditions"]["LorR.xlsx"][3]["delay"] = 1.49
        with self.assertRaisesRegex(ValueError, "at least 1.54 seconds.*latest condition tone"):
            settings.validate_settings(self.config)
        self.config["necker_seconds"] = 1.54
        settings.validate_settings(self.config)

    def test_fixed_demo_timing_caps_tone_duration(self):
        self.config["tone_seconds"] = 1.81
        self.config["conditioning_seconds"] = 3
        self.config["necker_seconds"] = 3
        with self.assertRaisesRegex(ValueError, "Tone component duration.*no greater than 1.8"):
            settings.validate_settings(self.config)
        self.config["tone_seconds"] = 1.8
        settings.validate_settings(self.config)

    def test_reference_practice_omits_late_tones_without_rejecting_defaults(self):
        self.assertGreater(max(row["delay"] for row in self.config["conditions"]["LorR.xlsx"]),
                           self.config["practice_seconds"])
        settings.validate_settings(self.config)

    def test_decimal_rounding_does_not_reject_a_fitting_tone(self):
        self.config["necker_seconds"] = 0.3
        self.config["tone_seconds"] = 0.2
        for row in self.config["conditions"]["LorR.xlsx"]:
            row["delay"] = 0.1
        settings.validate_settings(self.config)

    def test_asset_paths_require_files_and_allow_absolute_files(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.config["conditions"]["LorR.xlsx"][0]["Sound"] = str(directory)
            with self.assertRaisesRegex(ValueError, "LorR.xlsx, row 1, Sound file does not exist"):
                settings.validate_settings(self.config)
            asset = directory / "custom.wav"
            asset.write_bytes(b"placeholder file; this check validates paths only")
            self.config["conditions"]["LorR.xlsx"][0]["Sound"] = str(asset)
            self.assertEqual(settings.validate_settings(self.config)["conditions"]["LorR.xlsx"][0]["Sound"], str(asset))
            self.config["output_dir"] = str(asset)
            with self.assertRaisesRegex(ValueError, "must be a directory"):
                settings.validate_settings(self.config)


class SettingsPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "session-settings.json"

    def test_missing_settings_load_defaults_without_creating_a_file(self):
        self.assertEqual(settings.load_settings(self.path), settings.default_settings())
        self.assertFalse(self.path.exists())

    def test_malformed_json_is_reported_and_left_untouched(self):
        original = b'{"volume": 0.5, invalid json\r\n'
        self.path.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "Cannot read settings"):
            settings.load_settings(self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_valid_json_with_invalid_settings_is_left_untouched(self):
        config = settings.default_settings()
        config["volume"] = "loud"
        original = json.dumps(config).encode("utf-8")
        self.path.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "Invalid settings"):
            settings.load_settings(self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_atomic_round_trip_preserves_edited_conditions_and_calibration(self):
        config = settings.default_settings()
        config["conditions"]["LorR.xlsx"][0]["delay"] = 0.33
        config["practice_reps"] = 2
        config["monitor_width_cm"] = "53"
        config["monitor_distance_cm"] = "60"
        saved = settings.save_settings(config, self.path)
        self.assertEqual(settings.load_settings(self.path), saved)
        self.assertEqual(saved["conditions"]["LorR.xlsx"][0]["delay"], 0.33)
        self.assertEqual(saved["monitor_width_cm"], 53.0)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_failed_replacement_keeps_previous_settings_and_removes_temporary_file(self):
        original = settings.default_settings()
        settings.save_settings(original, self.path)
        original_bytes = self.path.read_bytes()
        changed = deepcopy(original)
        changed["practice_reps"] = 3
        with patch.object(settings.os, "replace", side_effect=PermissionError("Simulated locked destination")):
            with self.assertRaisesRegex(ValueError, "Cannot save settings"):
                settings.save_settings(changed, self.path)
        self.assertEqual(self.path.read_bytes(), original_bytes)
        self.assertEqual(settings.load_settings(self.path), original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_invalid_update_does_not_replace_previous_settings(self):
        original = settings.default_settings()
        settings.save_settings(original, self.path)
        original_bytes = self.path.read_bytes()
        changed = deepcopy(original)
        changed["blank_max_frames"] = changed["blank_min_frames"]
        with self.assertRaises(ValueError):
            settings.save_settings(changed, self.path)
        self.assertEqual(self.path.read_bytes(), original_bytes)


if __name__ == "__main__":
    unittest.main()
