"""Opt-in Tk smoke checks: set NECKER_GUI_SMOKE=1 on a desktop session.

These briefly create the launcher and settings windows. Dialogs, settings writes,
and runtime launch are stubbed; no experiment, sound, or hardware is started.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

import gui

PARTICIPANT = {"participant_ID": "0012", "age": 25, "sex": "Female",
               gui.HANDEDNESS_KEY: "Right handed", "colorblind": False,
               "manual_removed_electrodes": []}


class _Result:
    status = "aborted"

    def read_text(self, **kwargs):
        return json.dumps({"status": self.status, "error": "Simulated engine error"})


class _Handle:
    def __init__(self):
        self.session_dir = PROJECT / "data" / "test-placeholder"
        self.log_path = self.session_dir / "runner.log"
        self.result_path = _Result()
        self.code = None
        self.stopped = False

    def poll(self):
        return self.code

    def request_stop(self):
        self.stopped = True


@unittest.skipUnless(os.environ.get("NECKER_GUI_SMOKE") == "1", "Opt-in desktop Tk smoke")
class GuiSmokeTests(unittest.TestCase):
    def setUp(self):
        self.patches = [
            patch.object(gui, "load_settings", side_effect=gui.default_settings),
            patch.object(gui, "save_settings"),
            patch.object(gui.messagebox, "showerror"),
            patch.object(gui.messagebox, "showinfo"),
            patch.object(gui.messagebox, "askyesno", return_value=True),
            patch.object(gui.NeckerApp, "_participant_details", return_value=PARTICIPANT),
            patch.object(gui.NeckerApp, "_confirm_recording", return_value=True),
        ]
        mocks = [p.start() for p in self.patches]
        self.saved, self.error = mocks[1], mocks[2]
        self.participant_dialog, self.recording_dialog = mocks[5], mocks[6]
        self.app = gui.NeckerApp()

    def tearDown(self):
        if self.app.winfo_exists():
            for callback in self.app.tk.call("after", "info"):
                # Leave each widget's registered Tcl command for its own
                # destroy() to remove; callbacks belong to several widgets.
                self.app.tk.call("after", "cancel", callback)
            self.app.destroy()
        for p in reversed(self.patches):
            p.stop()

    def _assert_controls_fit(self, parent):
        for widget in parent.winfo_children():
            if not widget.winfo_ismapped():
                continue
            if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Button, ttk.Label, ttk.Checkbutton)):
                self.assertGreaterEqual(widget.winfo_x(), 0, str(widget))
                self.assertLessEqual(widget.winfo_x() + widget.winfo_width(), parent.winfo_width() + 1, str(widget))
                if isinstance(widget, (ttk.Label, ttk.Button, ttk.Checkbutton)):
                    self.assertGreaterEqual(widget.winfo_width() + 1, widget.winfo_reqwidth(), str(widget))
                    self.assertGreaterEqual(widget.winfo_height() + 1, widget.winfo_reqheight(), str(widget))
            self._assert_controls_fit(widget)

    def test_minimum_layout_and_all_settings_tabs(self):
        self.app.geometry("680x520")
        self.app.update()
        self._assert_controls_fit(self.app)
        self.app.open_settings()
        dialog = self.app._settings_dialog
        dialog.geometry("680x470")
        for tab in dialog.notebook.tabs():
            dialog.notebook.select(tab)
            self.app.update()
            self._assert_controls_fit(dialog)
            self.assertLessEqual(dialog.footer.winfo_y() + dialog.footer.winfo_height(), dialog.winfo_height())
            for button in dialog.footer.buttons:
                self.assertTrue(button.winfo_viewable())
                self.assertLessEqual(button.winfo_y() + button.winfo_height(), dialog.footer.winfo_height())
        conditions = dialog.editors["LorR.xlsx"].master
        for tab in conditions.tabs():
            conditions.select(tab)
            self.app.update()
            self._assert_controls_fit(dialog)

    def test_settings_at_large_text_scale(self):
        style = ttk.Style(self.app)
        style.configure(".", font=("Segoe UI", 16))
        style.configure("Primary.TButton", font=("Segoe UI", 16, "bold"))
        self.app.open_settings()
        dialog = self.app._settings_dialog
        dialog.geometry("680x470")
        for tab in dialog.notebook.tabs():
            dialog.notebook.select(tab)
            self.app.update()
            self._assert_controls_fit(dialog)
        self.assertGreater(dialog.footer.winfo_height(), 50)

    def test_serial_port_is_disabled_and_cannot_be_changed(self):
        self.app.open_settings()
        dialog = self.app._settings_dialog
        entry = dialog.serial_port_control
        self.assertTrue(entry.instate(["disabled"]))
        entry.delete(0, "end")
        entry.insert(0, "COM9")
        self.assertEqual(entry.get(), "COM3")
        dialog.variables["serial_port"].set("COM9")
        dialog.save()
        self.error.assert_called_once()
        self.saved.assert_not_called()

    def test_settings_are_staged_validated_and_saved(self):
        original = copy.deepcopy(self.app.config)
        self.app.open_settings()
        dialog = self.app._settings_dialog
        dialog.variables["baseline_blocks"].set("bad")
        dialog.save()
        self.error.assert_called_once()
        self.saved.assert_not_called()
        self.assertEqual(self.app.config, original)
        dialog.variables["baseline_blocks"].set("2")
        dialog.variables["monitor_width_cm"].set("52")
        dialog.variables["monitor_distance_cm"].set("60")
        self.assertEqual(dialog.collect()["monitor_width_cm"], 52.0)
        table = dialog.editors["LorR.xlsx"]
        count = len(table.rows)
        table.duplicate_row()
        self.assertEqual(len(table.rows), count + 1)
        table.remove_row()
        self.assertEqual(len(table.rows), count)
        dialog.restore_defaults()
        self.assertEqual(dialog.collect(), original)
        dialog.save()
        self.saved.assert_called_once_with(original)
        self.assertEqual(self.app.config, original)

    def test_background_launch_stop_and_result_states(self):
        handle = _Handle()
        self.app.withdraw()
        with patch.object(gui.runtime, "start_session", return_value=handle):
            self.app.start()
            deadline = time.monotonic() + 2
            while self.app.handle is None and time.monotonic() < deadline:
                self.app.update()
                time.sleep(0.01)
        self.assertIs(self.app.handle, handle)
        self.assertEqual(str(self.app.start_button.cget("state")), "disabled")
        self.assertEqual(str(self.app.settings_button.cget("state")), "disabled")
        self.app.stop()
        self.assertTrue(handle.stopped)
        self.assertEqual(str(self.app.stop_button.cget("state")), "disabled")
        handle.code = 0
        for status, badge in (("aborted", "STOPPED"), ("completed", "COMPLETE"), ("failed", "FAILED")):
            handle.result_path.status = status
            self.app._poll_session()
            self.assertEqual(self.app.badge.cget("text"), badge)
        self.assertEqual(str(self.app.start_button.cget("state")), "normal")
        self.error.assert_called_once()

    def test_cancel_demographics_or_recording_never_launches(self):
        with patch.object(gui.runtime, "start_session") as launch:
            self.participant_dialog.return_value = None
            self.app.start()
            self.recording_dialog.assert_not_called()
            self.participant_dialog.return_value = PARTICIPANT
            self.recording_dialog.return_value = False
            self.app.start()
            launch.assert_not_called()
        self.assertFalse(self.app.busy)
        self.assertFalse(self.app.start_button.instate(["disabled"]))

    def test_demographics_then_recording_on_every_launch(self):
        order = []
        self.participant_dialog.side_effect = lambda: order.append("participant") or PARTICIPANT
        self.recording_dialog.side_effect = lambda: order.append("recording") or True
        with patch.object(gui.runtime, "start_session", side_effect=RuntimeError("test failure")) as launch:
            for _ in range(2):
                self.app.start()
                deadline = time.monotonic() + 3
                while self.app.busy and time.monotonic() < deadline:
                    self.app.update()
                    time.sleep(.01)
            self.assertEqual(order, ["participant", "recording"] * 2)
            self.assertEqual(launch.call_count, 2)
            self.assertIs(launch.call_args.kwargs["recording_confirmed"], True)

    def test_demographics_validation_and_numeric_input(self):
        dialog = gui.ParticipantDialog(self.app)
        dialog.geometry("680x470")
        self.app.update()
        self._assert_controls_fit(dialog)
        dialog.accept()
        self.assertIsNone(dialog.result)
        self.assertIn("digits", dialog.error_text.get())
        entry = dialog.controls["participant_ID"]
        entry.insert(0, "bad")
        self.assertEqual(entry.get(), "")
        entry.insert(0, "0012")
        dialog.variables["age"].set("121")
        dialog.accept()
        self.assertIn("1 to 120", dialog.error_text.get())
        for key, value in PARTICIPANT.items():
            if key not in {"colorblind", "manual_removed_electrodes"}:
                dialog.variables[key].set(value)
        dialog.accept()
        self.assertIn("colorblind", dialog.error_text.get())
        for key in ("sex", gui.HANDEDNESS_KEY, "colorblind"):
            self.assertTrue(dialog.controls[key].instate(["readonly"]))
        dialog.variables["colorblind"].set("No")
        dialog.accept()
        self.assertEqual(dialog.result, PARTICIPANT)

    def test_sophia_requires_exact_confirmation(self):
        dialog = gui.BioSemiRecordingConfirmationDialog(self.app)
        self.app.update()
        self._assert_controls_fit(dialog)
        for value in ("", "yes", "Confirmed", "not confirm"):
            dialog.confirmation.set(value)
            self.assertTrue(dialog.continue_button.instate(["disabled"]))
            dialog.accept()
            self.assertFalse(dialog.result)
        dialog.confirmation.set("  cOnFiRm  ")
        self.assertFalse(dialog.continue_button.instate(["disabled"]))
        dialog.accept()
        self.assertTrue(dialog.result)

    def test_explicit_sophia_disable_skips_only_recording_check(self):
        self.app.config["sophia_mode"] = False
        with patch.object(gui.runtime, "start_session", side_effect=RuntimeError("test failure")) as launch:
            self.app.start()
            deadline = time.monotonic() + 3
            while self.app.busy and time.monotonic() < deadline:
                self.app.update()
                time.sleep(.01)
            self.participant_dialog.assert_called_once()
            self.recording_dialog.assert_not_called()
            self.assertIs(launch.call_args.kwargs["recording_confirmed"], False)

    def test_test_mode_skips_hardware_prompts_and_restores_normal_launch(self):
        self.app.open_settings()
        dialog = self.app._settings_dialog
        dialog.variables["test_mode"].set(True)
        dialog.save()
        self.assertTrue(self.app.config["test_mode"])
        self.assertTrue(self.app.config["serial_enabled"])
        self.assertTrue(self.app.config["sophia_mode"])
        self.assertEqual(self.app.start_button.cget("text"), "Launch Test Experiment")
        self.assertEqual(self.app.badge.cget("text"), "TEST MODE")
        self.assertIn("test_runs", self.app.output_text.get())
        with patch.object(gui.runtime, "start_session", side_effect=RuntimeError("test failure")) as launch, \
             patch.object(self.app, "_confirm_test_mode", return_value=True) as acknowledge:
            self.app.start()
            deadline = time.monotonic() + 3
            while self.app.busy and time.monotonic() < deadline:
                self.app.update()
                time.sleep(.01)
            acknowledge.assert_called_once()
            self.participant_dialog.assert_not_called()
            self.recording_dialog.assert_not_called()
            self.assertIsNone(launch.call_args.args[1])
            self.assertFalse(launch.call_args.kwargs["recording_confirmed"])
            self.app.config["test_mode"] = False
            self.app.refresh_summary()
            self.assertEqual(self.app.start_button.cget("text"), "Launch Experiment")
            self.app.start()
            deadline = time.monotonic() + 3
            while self.app.busy and time.monotonic() < deadline:
                self.app.update()
                time.sleep(.01)
            self.participant_dialog.assert_called_once()
            self.recording_dialog.assert_called_once()
            self.assertTrue(launch.call_args.kwargs["recording_confirmed"])

    def test_cancel_test_acknowledgment_never_launches(self):
        self.app.config["test_mode"] = True
        with patch.object(self.app, "_confirm_test_mode", return_value=False), \
             patch.object(gui.runtime, "start_session") as launch:
            self.app.start()
            launch.assert_not_called()
            self.participant_dialog.assert_not_called()
            self.recording_dialog.assert_not_called()
            self.assertFalse(self.app.busy)


if __name__ == "__main__":
    unittest.main()
