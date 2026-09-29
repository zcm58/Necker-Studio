"""Opt-in desktop regression: real PsychoPy glyph bounds and frame captures.

Run with the project's Python; opens full-screen then smaller test windows.
No keyboard, serial, audio, experiment clock or participant records are used.
"""
import ast
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from adapter import build_source
from settings import default_settings
from presentation import fit_presentation, bounds, safe_size, TEXT_NAMES, IMAGE_NAMES


def main():
    import os
    from psychopy import monitors, visual
    os.chdir(PROJECT / 'assets')
    output = PROJECT / '.verification' / 'presentation_margins'
    output.mkdir(parents=True, exist_ok=True)
    tree = ast.parse(build_source(default_settings()))
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    constructors = [n for n in run.body if isinstance(n, ast.Assign)
                    and isinstance(n.value, ast.Call)
                    and ast.unparse(n.value.func) in ('visual.TextStim', 'visual.ImageStim')]
    code = compile(ast.Module(body=constructors, type_ignores=[]), '<presentation-test>', 'exec')
    monitor = monitors.Monitor('necker_margin_verification', width=53, distance=80)
    monitor.setSizePix((1920, 1080))
    report = []
    for size, full_screen in (((1920, 1080), True), ((800, 600), False), ((1280, 720), False)):
        win = visual.Window(size=size, fullscr=full_screen, monitor=monitor,
                            units='height', color=[.65, .65, .65], checkTiming=False)
        try:
            components = {'visual': visual, 'win': win}
            exec(code, components)
            original = {n: (list(components[n].size), list(components[n].pos), components[n].units)
                        for n in ('image_2', 'image_3', 'image_4')}
            fit_presentation(win, components)
            actual = {n: (list(components[n].size), list(components[n].pos), components[n].units)
                      for n in original}
            assert actual == original, (original, actual)
            w, h = safe_size(win.size)
            groups = [('text_22', 'image_9'), ('text_24', 'image_10')]
            groups += [(n,) for n in (*TEXT_NAMES, *IMAGE_NAMES)]
            records = {}
            for group in groups:
                for name in group:
                    stim = components[name]
                    l, b, r, t = bounds(stim)
                    assert l >= -w / 2 - 1 and r <= w / 2 + 1, (name, l, r, w)
                    assert b >= -h / 2 - 1 and t <= h / 2 + 1, (name, b, t, h)
                    records[name] = [l, b, r, t]
                    stim.draw()
                if len(group) == 2:
                    assert records[group[0]][1] > records[group[1]][3]
                win.flip()
                win.getMovieFrame(buffer='front')
                win.movieFrames[-1].save(output / f'{size[0]}x{size[1]}_{group[0]}.png')
                win.movieFrames.clear()
            report.append({'size': list(win.size.astype(int)), 'full_screen': full_screen,
                           'bounds': records, 'trial_geometry_preserved': True})
        finally:
            win.close()
    (output / 'report.json').write_text(json.dumps(report, indent=2, default=int))
    print('Presentation margins passed at 1920x1080 fullscreen, 800x600 and 1280x720; 53 cm / 80 cm calibration.')


if __name__ == '__main__':
    main()
