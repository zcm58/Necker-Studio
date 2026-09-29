"""Regression checks for screen margins and initialization-only layout."""
import ast
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapter import build_source
from settings import default_settings
from window_layout import window_geometry


class LayoutTests(unittest.TestCase):
    def test_all_four_edges_leave_room_on_small_and_offset_monitors(self):
        for area in ((0, 0, 1920, 1040), (0, 0, 800, 560), (-1280, -200, 0, 824)):
            for center in (None, (-4000, -4000), (4000, 4000)):
                with self.subTest(area=area, center=center):
                    w, h, x, y = window_geometry(960, 760, area, center)
                    self.assertGreaterEqual(x, area[0] + 32)
                    self.assertGreaterEqual(y, area[1] + 32)
                    self.assertLessEqual(x + w + 20, area[2] - 32)
                    self.assertLessEqual(y + h + 72, area[3] - 32)

    def test_layout_is_once_before_clock_and_never_inside_frame_loops(self):
        tree = ast.parse(build_source(default_settings()))
        run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
        calls = [n for n in ast.walk(run) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'fit_presentation']
        self.assertEqual(len(calls), 1)
        clock = next(n for n in run.body if isinstance(n, ast.If)
                     and ast.unparse(n.test) == 'globalClock is None')
        self.assertLess(calls[0].lineno, clock.lineno)
        self.assertTrue(any(isinstance(n, ast.Expr) and n.value is calls[0] for n in run.body))
