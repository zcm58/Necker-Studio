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
        ]
        mocks = [p.start() for p in self.patches]
        self.saved, self.error = mocks[1], mocks[2]
        self.app = gui.NeckerApp()

    def tearDown(self):
        if self.app.winfo_exists():
            for callback in self.app.tk.call("after", "info"):
                self.app.after_cancel(callback)
            self.app.destroy()
        for p in reversed(self.patches):
            p.stop()

    def _assert_controls_fit(self, parent):
        for widget in parent.winfo_children():
            if not widget.winfo_ismapped():
                continue
            if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Button)):
                self.assertGreaterEqual(widget.winfo_x(), 0, str(widget))
                self.assertLessEqual(widget.winfo_x() + widget.winfo_width(), parent.winfo_width() + 1, str(widget))
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
        conditions = dialog.editors["LorR.xlsx"].master
        for tab in conditions.tabs():
            conditions.select(tab)
            self.app.update()
            self._assert_controls_fit(dialog)

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
        self.app.participant["participant_ID"].set("smoke")
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

    def test_original_freeform_participant_fields(self):
        handle = _Handle()
        self.app.withdraw()
        self.app.participant["handedness (left or right)"].set("ambidextrous")
        with patch.object(gui.runtime, "start_session", return_value=handle) as launch:
            self.app.start()
            deadline = time.monotonic() + 2
            while self.app.handle is None and time.monotonic() < deadline:
                self.app.update()
                time.sleep(0.01)
        launch.assert_called_once()
        participant = launch.call_args.args[1]
        self.assertEqual(participant["participant_ID"], "")
        self.assertEqual(participant["handedness (left or right)"], "ambidextrous")
        self.error.assert_not_called()
        handle.code = 0
        self.app._set_busy(False)
        self.assertEqual(str(self.app.participant_controls[-1].cget("state")), "normal")


if __name__ == "__main__":
    unittest.main()
