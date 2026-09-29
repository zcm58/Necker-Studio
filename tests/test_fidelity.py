"""Protocol regression checks; no PsychoPy import, window, or hardware required."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import sys
import unittest


PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from adapter import SerialConnection, build_source
from settings import condition_rows, default_settings


REFERENCE_SHA256 = "0a0ce03f9fc72d15bf38b5319e6b8819df9c16f708bca9c4df4aebcc3d504204"


def call_name(node):
    return ast.unparse(node.func) if isinstance(node, ast.Call) else ""


def keyword(call, name):
    return next(item.value for item in call.keywords if item.arg == name)


def handlers(tree):
    return {
        ast.literal_eval(keyword(node, "name")): node
        for node in ast.walk(tree)
        if call_name(node) == "data.TrialHandler2"
    }


def protocol_flow(tree):
    """Extract routine order and loop nesting, ignoring frame-update machinery."""
    run = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run")
    loop_names = set(handlers(tree))

    def visit(body):
        result = []
        for node in body:
            if isinstance(node, ast.Assign) and call_name(node.value) == "data.Routine":
                result.append(ast.literal_eval(keyword(node.value, "name")))
            elif isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id in loop_names:
                result.append((node.iter.id, visit(node.body)))
        return result

    return visit(run.body)


def component_durations(tree):
    """Collect stop thresholds of the form component.tStartRefresh + seconds."""
    values = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
            continue
        if not isinstance(node.left, ast.Attribute) or node.left.attr != "tStartRefresh":
            continue
        if isinstance(node.left.value, ast.Name) and isinstance(node.right, ast.Constant):
            values.setdefault(node.left.value.id, set()).add(node.right.value)
    return values


class ProtocolFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = default_settings()
        cls.source = build_source(cls.config)
        cls.tree = ast.parse(cls.source)

    def test_reference_is_the_audited_latest_builder_script(self):
        reference = PROJECT / "reference" / "experiment_source.py"
        self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(), REFERENCE_SHA256)

    def test_default_protocol_order_and_nested_blocks(self):
        self.assertEqual(protocol_flow(self.tree), [
            "Intro", "intro2", "sound_test", "instructions", "cross", "Practice_run",
            ("trials_9", ["blank_cross", "NeckerBaseline", "blank"]),
            "Baseline", "cross",
            ("trials_6", [("trials_3", ["blank_cross", "Base_trigger", "Necker", "blank"]), "break_2"]),
            "cross", "Instr_gonogo", "last_instructions",
            ("trials_7", ["dontpress1"]), ("trials_8", ["pressEx"]), "ready_",
            ("trials_5", [("trials", ["blank_cross", "trial", "goNogo"]), "break_2"]),
            "instructions", "cross",
            ("trials_4", [("trials_2", ["blank_cross", "conditioned_trigger", "Necker", "blank"]), "break_2"]),
            "Thanks",
        ])

    def test_default_randomization_repetitions_and_trial_counts(self):
        loops = handlers(self.tree)
        expected = {
            "trials_9": (1, "random"), "trials_6": (5, "random"),
            "trials_3": (3, "random"), "trials_7": (1, "sequential"),
            "trials_8": (2, "sequential"), "trials_5": (5, "random"),
            "trials": (4, "random"), "trials_4": (5, "random"),
            "trials_2": (3, "random"),
        }
        self.assertEqual(set(loops), set(expected))
        for name, (repetitions, method) in expected.items():
            with self.subTest(loop=name):
                self.assertEqual(ast.literal_eval(keyword(loops[name], "nReps")), repetitions)
                self.assertEqual(ast.literal_eval(keyword(loops[name], "method")), method)
                self.assertIsNone(ast.literal_eval(keyword(loops[name], "seed")))
        reps = lambda name: ast.literal_eval(keyword(loops[name], "nReps"))
        necker_rows = len(condition_rows(self.config, "LorR.xlsx"))
        conditioning_rows = len(condition_rows(self.config, "SoundA.xlsx"))
        counts = [
            reps("trials_9") * necker_rows,
            reps("trials_6") * reps("trials_3") * necker_rows,
            reps("trials_5") * reps("trials") * conditioning_rows,
            reps("trials_4") * reps("trials_2") * necker_rows,
        ]
        self.assertEqual(counts, [8, 120, 120, 120])
        self.assertEqual(sum(counts), 368)

    def test_repetition_settings_change_only_the_requested_phase_lengths(self):
        config = default_settings()
        changes = {
            "practice_reps": ("trials_9", 2), "baseline_blocks": ("trials_6", 3),
            "baseline_reps": ("trials_3", 4), "conditioning_blocks": ("trials_5", 2),
            "conditioning_reps": ("trials", 5), "post_blocks": ("trials_4", 4),
            "post_reps": ("trials_2", 2), "no_go_demo_reps": ("trials_7", 2),
            "go_demo_reps": ("trials_8", 3),
        }
        config.update({key: value for key, (_, value) in changes.items()})
        tree = ast.parse(build_source(config))
        loops = handlers(tree)
        for key, (loop, value) in changes.items():
            with self.subTest(setting=key):
                self.assertEqual(ast.literal_eval(keyword(loops[loop], "nReps")), value)
        self.assertEqual(protocol_flow(tree), protocol_flow(self.tree))
        self.assertEqual(component_durations(tree), component_durations(self.tree))

    def test_condition_tables_match_original_workbooks_without_needing_excel(self):
        self.assertEqual(condition_rows(self.config, "LorR.xlsx"), [
            {"Sound": sound, "delay": delay, "image": "Necker.png", "choice": choice, "ISI": None}
            for sound, delay, choice in [
                ("440.wav", 0, "LoR.png"), ("0.wav", 0, "RoL.png"),
                ("440.wav", 0, "RoL.png"), ("0.wav", 0, "LoR.png"),
                ("440.wav", .2, "LoR.png"), ("440.wav", .2, "RoL.png"),
                ("440.wav", .85, "LoR.png"), ("440.wav", .85, "RoL.png"),
            ]
        ])
        self.assertEqual(condition_rows(self.config, "SoundA.xlsx"), [
            dict(zip(("Sound", "text", "image", "choice", "correct", "GoNoGo"), row))
            for row in [
                ("440.wav", "Left", "L.png", "LoR.png", "Left", "None"),
                ("440.wav", "Right", "R.png", "RoL.png", "Left", "space"),
                ("440.wav", "Left", "L.png", "RoL.png", "Right", "None"),
                ("440.wav", "Right", "R.png", "LoR.png", "Right", "space"),
                ("0.wav", "Left", "L.png", "LoR.png", "Left", "None"),
                ("0.wav", "Right", "R.png", "RoL.png", "Left", "None"),
            ]
        ])
        self.assertEqual(condition_rows(self.config, "SoundEx.xlsx", "0:3"), [
            {"Sound": "440.wav", "text": "Left", "image": "L.png"},
            {"Sound": "0.wav", "text": "Right", "image": "R.png"},
            {"Sound": "0.wav", "text": "Left", "image": "L.png"},
        ])
        self.assertEqual(condition_rows(self.config, "SoundEx.xlsx", "3"), [
            {"Sound": "440.wav", "text": "Right", "image": "R.png"},
        ])

    def test_live_trial_lists_use_saved_settings_and_demo_row_selections(self):
        calls = [node for node in ast.walk(self.tree) if call_name(node) == "get_conditions"]
        selections = []
        for node in calls:
            filename = ast.literal_eval(node.args[0])
            selection = next((ast.literal_eval(item.value) for item in node.keywords if item.arg == "selection"), None)
            selections.append((filename, selection))
        self.assertCountEqual(selections, [
            ("LorR.xlsx", None), ("LorR.xlsx", None), ("LorR.xlsx", None),
            ("SoundA.xlsx", None), ("SoundEx.xlsx", "0:3"), ("SoundEx.xlsx", "3"),
        ])
        names = {call_name(node) for node in ast.walk(self.tree) if isinstance(node, ast.Call)}
        self.assertNotIn("data.importConditions", names)
        self.assertNotIn("serial.Serial", names)
        self.assertIn("open_serial", names)

    def test_default_stimulus_and_response_timing_matches_protocol(self):
        expected = {
            "image_4": .15, "text_7": .8, "image_3": .15, "text_5": 1.5,
            "sound_2": .05, "image4": 3, "key_resp": 3, "text_8": 3,
            "image_2": .15, "sound_1": .05, "text_2": 1.5, "G0_NoGo_key": 1.5,
            "key_resp_4": 1.4, "text_10": 1.4, "text_6": 1,
        }
        actual = component_durations(self.tree)
        for component, seconds in expected.items():
            with self.subTest(component=component):
                self.assertEqual(actual.get(component), {seconds})
        # Existing jitter re-draws on each frame; sampling once changes the protocol.
        jitter = [node for node in ast.walk(self.tree) if isinstance(node, ast.If)
                  and any(call_name(child) == "randint" for child in ast.walk(node.test))]
        self.assertEqual(len(jitter), 4)
        for check in jitter:
            draw = next(node for node in ast.walk(check.test) if call_name(node) == "randint")
            self.assertEqual([ast.literal_eval(value) for value in draw.args], [62, 125])

    def test_keyboard_semantics_keep_queued_arrows_and_two_space_windows(self):
        clear_names = {
            node.args[0].value.id
            for node in ast.walk(self.tree)
            if call_name(node) == "win.callOnFlip" and node.args
            and isinstance(node.args[0], ast.Attribute) and node.args[0].attr == "clearEvents"
        }
        self.assertNotIn("key_resp", clear_names)
        self.assertIn("G0_NoGo_key", clear_names)
        self.assertIn("key_resp_4", clear_names)
        allowed = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "getKeys":
                if isinstance(node.func.value, ast.Name) and node.func.value.id in {"key_resp", "G0_NoGo_key", "key_resp_4"}:
                    allowed.setdefault(node.func.value.id, []).append(ast.literal_eval(keyword(node, "keyList")))
                    self.assertFalse(ast.literal_eval(keyword(node, "waitRelease")))
        self.assertEqual(allowed["key_resp"], [["left", "right"]] * 3)
        self.assertEqual(allowed["G0_NoGo_key"], [["space"]])
        self.assertEqual(allowed["key_resp_4"], [["space"]])

    def test_custom_timing_updates_each_occurrence_and_still_compiles(self):
        config = default_settings()
        config.update({
            "stimulus_seconds": .25, "practice_seconds": 1.1, "necker_seconds": 2.2,
            "response_seconds": 4.2, "conditioning_seconds": 2.5, "gonogo_seconds": 1.8,
            "fixation_seconds": .6, "blank_min_frames": 70, "blank_max_frames": 150,
            "tone_seconds": .08, "volume": .4, "cube_width_deg": 7, "cube_height_deg": 6,
        })
        source = build_source(config)
        compile(source, "configured_experiment.py", "exec")
        tree = ast.parse(source)
        expected = {
            "image_4": .25, "text_7": 1.1, "image_3": .25, "text_5": 2.2,
            "sound_2": .08, "image4": 4.2, "key_resp": 4.2, "text_8": 4.2,
            "image_2": .25, "sound_1": .08, "text_2": 2.5, "G0_NoGo_key": 2.5,
            "key_resp_4": 1.8, "text_10": 1.8, "text_6": .6,
        }
        actual = component_durations(tree)
        for component, seconds in expected.items():
            with self.subTest(component=component):
                self.assertEqual(actual.get(component), {seconds})
        draws = [node for node in ast.walk(tree) if call_name(node) == "randint"]
        self.assertEqual(len(draws), 4)
        for draw in draws:
            self.assertEqual([ast.literal_eval(value) for value in draw.args], [70, 150])
        for node in ast.walk(tree):
            if call_name(node) == "visual.ImageStim":
                if ast.literal_eval(keyword(node, "name")) in {"image_2", "image_3", "image_4"}:
                    self.assertEqual(tuple(ast.literal_eval(keyword(node, "size"))), (7, 6))
        self.assertEqual(protocol_flow(tree), protocol_flow(self.tree))


class SerialOwnershipTests(unittest.TestCase):
    def test_duplicate_builder_opens_reuse_one_exclusive_serial_handle(self):
        config = default_settings()
        config.update({"serial_enabled": True, "serial_port": "COM3", "serial_baud": 115200})
        opened = []
        state = {"active": False}

        class ExclusivePort:
            def __init__(self, *args, **kwargs):
                if state["active"]:
                    raise PermissionError("COM3 is already open")
                state["active"] = True
                self.close_calls = 0
                self.writes = []
                opened.append((args, kwargs, self))

            def write(self, payload):
                self.writes.append(payload)
                return len(payload)

            def close(self):
                self.close_calls += 1
                state["active"] = False

        connection = SerialConnection(config, factory=ExclusivePort)
        first = connection.open()
        second = connection.open()
        self.assertIs(first, second)
        self.assertEqual(len(opened), 1)
        first.write(b"\x01")
        second.write(b"\x02")
        self.assertEqual(first.writes, [b"\x01", b"\x02"])
        connection.close()
        connection.close()
        self.assertEqual(first.close_calls, 1)
        self.assertFalse(state["active"])


if __name__ == "__main__":
    unittest.main()
