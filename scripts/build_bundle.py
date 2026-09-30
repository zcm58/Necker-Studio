"""Assemble a relocatable copy of the verified CPython/PsychoPy environment."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

PROJECT = Path(__file__).resolve().parents[1]
APP_FILES = ('main.py', 'gui.py', 'settings.py', 'runtime.py', 'adapter.py', 'triggers.py',
             'updates.py', 'update_ui.py', 'participant.py', 'presentation.py', 'window_layout.py', 'app_paths.py',
             'defaults.json', 'README.md', 'requirements.txt', 'requirements.in', 'pyproject.toml')


def ignore(directory, names):
    return [n for n in names if n == '__pycache__' or n.endswith(('.pyc', '.pyo'))
            or n in ('_virtualenv.py', '_virtualenv.pth', 'direct_url.json')]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT / 'build') or output.exists():
        raise SystemExit('Choose a new output folder inside this project\'s build directory.')
    version = tomllib.loads((PROJECT / 'pyproject.toml').read_text())['project']['version']
    if sys.version_info[:3] != (3, 12, 14) or Path(sys.prefix).resolve() != PROJECT / '.venv':
        raise SystemExit('Build with the verified .venv Python 3.12.14.')
    subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=PROJECT, text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=PROJECT, text=True).strip():
        raise SystemExit('Commit source changes before building a release.')
    # A release must pass the transport, normal/test-mode selection, source-site
    # and worker error/export regressions; none of these tests touch hardware.
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                    '-p', 'test_*.py', '-q'], cwd=PROJECT, check=True)
    runtime = output / 'runtime'
    runtime.mkdir(parents=True)
    base = Path(sys.base_prefix)
    for folder in ('DLLs', 'include', 'libs', 'tcl'):
        shutil.copytree(base / folder, runtime / folder, ignore=ignore)
    def ignore_base(directory, names):
        return ignore(directory, names) + (['site-packages'] if Path(directory) == base / 'Lib' else [])
    shutil.copytree(base / 'Lib', runtime / 'Lib', ignore=ignore_base)
    for path in base.iterdir():
        if path.is_file() and (path.suffix.lower() in ('.exe', '.dll') or path.name == 'LICENSE.txt'):
            shutil.copy2(path, runtime / path.name)
    shutil.copytree(Path(sys.prefix) / 'Lib' / 'site-packages', runtime / 'Lib' / 'site-packages', ignore=ignore)
    app = output / 'app'
    app.mkdir()
    for name in APP_FILES:
        shutil.copy2(PROJECT / name, app / name)
    for name in ('assets', 'reference'):
        shutil.copytree(PROJECT / name, app / name, ignore=ignore)
    shutil.copy2(PROJECT / 'packaging' / 'bootstrap.py', app / 'bootstrap.py')
    notices = output / 'licenses'
    notices.mkdir()
    shutil.copytree(PROJECT / 'vendor', notices / 'vendor', ignore=ignore)
    shutil.copy2(base / 'LICENSE.txt', notices / 'PYTHON-LICENSE.txt')
    packages = sorted([{'name': d.metadata['Name'], 'version': d.version}
                       for d in metadata.distributions()], key=lambda p: p['name'].lower())
    release = {'version': version, 'source_commit': commit, 'python': sys.version,
               'built_utc': datetime.now(timezone.utc).isoformat(), 'packages': packages}
    (app / 'release.json').write_text(json.dumps(release, indent=2), encoding='utf-8')
    (notices / 'README.txt').write_text(
        'This distribution contains CPython and third-party Python packages.\n'
        'Each package retains its license files in runtime/Lib/site-packages, including\n'
        'the *.dist-info/licenses directories. Python source modules are included.\n'
        'Local wheel provenance and licenses are in licenses/vendor.\n'
        'Exact package versions are listed in app/release.json.\n', encoding='utf-8')
    assembly = output.parent / 'AssemblyInfo.cs'
    assembly.write_text('using System.Reflection;\n'
        '[assembly: AssemblyTitle("Nicholas\'s Nice Necker Cube Experiment")]\n'
        f'[assembly: AssemblyVersion("{version}.0.0")]\n'
        f'[assembly: AssemblyFileVersion("{version}.0.0")]\n', encoding='utf-8')
    compiler = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')
    subprocess.run([str(compiler), '/nologo', '/target:winexe', '/platform:x64',
                    '/reference:System.Windows.Forms.dll', f'/out:{output / "NeckerExperiment.exe"}',
                    str(PROJECT / 'packaging' / 'launcher.cs'), str(assembly)], check=True)
    subprocess.run([str(compiler), '/nologo', '/target:exe', '/platform:x64',
                    '/reference:System.Windows.Forms.dll', f'/out:{output / "NeckerUpdater.exe"}',
                    str(PROJECT / 'packaging' / 'update_safety.cs'),
                    str(PROJECT / 'packaging' / 'updater.cs'), str(assembly)], check=True)
    subprocess.run([str(compiler), '/nologo', '/target:exe', '/platform:x64',
                    '/reference:System.Web.Extensions.dll', f'/out:{output.parent / "NeckerSetupVerifier.exe"}',
                    str(PROJECT / 'packaging' / 'update_safety.cs'),
                    str(PROJECT / 'packaging' / 'setup_verifier.cs')], check=True)
    probe = ('import sys, tkinter, psychopy, serial, pyWinhook, pyglet; '
             'assert sys.version_info[:3] == (3,12,14); '
             'assert psychopy.__version__ == "2026.2.4"; '
             'import psychopy.visual, psychopy.sound, psychopy.iohub; import triggers, updates, update_ui; '
             'print("Bundled Python, Tk, PsychoPy, audio, ioHub and serial imports passed.")')
    subprocess.run([str(runtime / 'python.exe'), '-E', '-s', '-B', '-c', probe], check=True, cwd=app)
    trigger_probe = (
        'from adapter import build_source; from settings import default_settings; '
        'from triggers import SerialConnection; from unittest.mock import Mock; '
        'c=default_settings(); build_source(c); p=Mock(); p.write.return_value=1; '
        's=SerialConnection(c, factory=Mock(return_value=p)); s.open(); '
        's.send(1, label="initial_baseline"); s.send(2, label="initial_conditioned"); '
        's.validate_completion(0); s.send(255); '
        'assert p.write.call_args.args == (bytes([255]),); s.close(); '
        'print("Packaged BioSemi trigger safeguards passed.")'
    )
    subprocess.run([str(runtime / 'python.exe'), '-E', '-s', '-B', '-c', trigger_probe], check=True, cwd=app)
    subprocess.run([str(runtime / 'python.exe'), '-E', '-s', '-B', '-m', 'pip', 'check'], check=True)
    manifest = {}
    for path in sorted(output.rglob('*')):
        if path.is_file():
            with path.open('rb') as stream:
                manifest[path.relative_to(output).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Verified bundle: {output}')


if __name__ == '__main__':
    main()
