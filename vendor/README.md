# Windows compatibility dependencies

These wheels keep PsychoPy 2026.2.4's existing keyboard and graphics backends usable on CPython 3.12 x64. Install them through `requirements.txt` from the repository root. They are project-local; no global packages are patched. `sha256.json` records the shipped wheel digests, checked by the setup script. Original license notices are included in both wheels and alongside this file.

## pyWinhook 1.6.2

- Input: [published PyPI source](https://files.pythonhosted.org/packages/ce/d1/6dcf4a17f425a5e3e2c011bac622dacae3128e96fd038b3e6f56c0e7a032/pyWinhook-1.6.2.zip). SHA256: `18fe2f63245d8a2f9d83f8d9c385e3695a6363badd50d492eb3e7f6f06a01c0c`.
- Build: [Windows CI run 36637569559](https://github.com/zcm58/Necker-Studio/actions/runs/36637569559), using `.github/workflows/build-windows-dependency.yml` on Windows x64, CPython 3.12, MSVC and SWIG.
- Compatibility change: compiler definition `/DPyInt_AsLong=PyLong_AsLong` maps the legacy Python 2 integer-conversion name to Python 3's equivalent. No hook event or timing logic is changed. The original Python/C sources are otherwise unmodified.
- Verification: the CI runner imported the installed hook; a local full experiment session initialized the ioHub keyboard backend and shut down successfully on Python 3.12.14.
- Wheel: `pywinhook-1.6.2-cp312-cp312-win_amd64.whl`.
- SHA256: `3c9d80ad0cde2395cf8f3c9a999df98fd0d49c18e2e02faea30b138b7d2a99fa`.

To build a fresh wheel, dispatch the **Build Windows keyboard dependency** workflow and download its artifact. Rebuilt compiled wheels may have a different binary checksum; review and update the manifest deliberately.

## Pyglet 1.4.11+necker1

- Input: [official Pyglet 1.4.11 wheel](https://files.pythonhosted.org/packages/b2/de/55594ab6496d6c08f511531502b614271c3120617b7068ba9b98d4284f04/pyglet-1.4.11-py2.py3-none-any.whl).
- Input SHA256: `8a8317fbb2bae145bd80f6d92d66b6dbbc9d13f1cbbed682ff55793a63003a46`.
- Build: run `python scripts/build_pyglet_wheel.py`. The script verifies the input hash and generates a deterministic wheel with a new RECORD.
- Compatibility change in `pyglet/font/win32.py`: `(ctypes.c_byte * (4 * width * height))()` becomes `(BYTE * (4 * width * height))()`. `BYTE` is the same Windows typedef used by the GDI+ call. Python 3.12 changed its signedness, making the old allocation fail ctypes argument validation.
- The only code change is that allocation. Distribution metadata uses local version `1.4.11+necker1`; the internal upstream version string remains `1.4.11`. The local version satisfies PsychoPy's `pyglet==1.4.11` dependency.
- Upstream reports: [PsychoPy #7589](https://github.com/psychopy/psychopy/issues/7589), [CPython #111150](https://github.com/python/cpython/issues/111150).
- Verification: real `TextStim` rendering throughout the complete accelerated experiment, with generated CSV, psydat and log outputs.
- SHA256: `424ae4bb9a286f0ec30919775a9499541f9076688e9e0471651c396b6bfe395d`.

No stimulus routine, frame loop, response window, or serial behavior is altered by either compatibility change. Hardware timing must still be validated on the acquisition machine.
