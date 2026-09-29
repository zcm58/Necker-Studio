# Nicholas's Nice Necker Cube Experiment

A standalone operator interface for `__NEW_NECKER.psyexp`, with a File > Settings dialog and an FPVS Studio inspired light interface. PsychoPy still performs stimulus presentation, audio, response collection, and timing. Builder is not needed to run or configure a session.

## Windows release 1.0

Download the x64 installer from [GitHub Releases](https://github.com/zcm58/Necker-Studio/releases/tag/v1.0).
It includes Python 3.12.14 and the pinned PsychoPy environment; no separate Python or PsychoPy installation is required.
The installer runs per user and creates a Start menu shortcut. A desktop shortcut is optional.
Installed settings and relative output folders live under `%LOCALAPPDATA%\NicholasNiceNeckerCubeExperiment`.
They persist across launches, reinstallations and uninstalling the application. An explicitly selected absolute output folder is retained.
The installed app starts with factory settings; configure the actual monitor calibration in File > Settings before collecting data.

## Run from PyCharm

This machine's project is **C:\Users\zcm58\PyCharmProjects\Necker-Studio**.

1. Open that folder in PyCharm.
2. Select the saved **Nicholas's Nice Necker Cube Experiment** run configuration and press Run, or right-click **main.py** and choose Run.

The project interpreter is **.venv\Scripts\python.exe**, running **Python 3.12.14** with **PsychoPy 2026.2.4**. Python itself lives in the project's ignored `.python` folder. Dependencies are installed in `.venv`; system site-packages are disabled. The launcher automatically prefers this local environment, including when main.py is launched by another Python installation.

The File > Settings dialog configures the experiment. No source, JSON, or spreadsheet edits are required. Serial is enabled on COM3 by default. The port is locked; disable serial explicitly for a session without that hardware.

Click **Launch Experiment** to open **Participant Information**. Like FPVS Studio, it requires a digits-only participant number (leading zeroes are retained), a whole-number age from 1 to 120, and selections for sex, handedness, and colorblind status. Sex offers Female/Male; handedness offers Right handed/Left handed/Ambidextrous. Optional manually removed electrodes are normalized and saved with the session. Participant details are requested afresh on every launch.

**Sophia Mode is enabled by default.** After demographics, the administrator must check that the BioSemi PC is recording and type **Confirm**. This is the same typed operator acknowledgment used in FPVS Studio; it does not automatically detect recording. Cancelling either dialog leaves the experiment stopped. The worker also rejects missing confirmation before opening PsychoPy or COM3. The confirmation is saved with that session and never reused for a later launch. Sophia Mode can be explicitly disabled in General settings for runs that do not require recording.

## Test mode

Open **File > Settings > General**, check **Enable test mode**, and click **Save settings**. The launcher displays **TEST MODE** and a **Launch Test Experiment** button. As in FPVS Studio, launching asks for a test-run acknowledgment instead of demographics and skips Sophia Mode. The COM3 connection is never opened, checked, or written to, even when the normal serial-trigger setting is enabled. Full-screen presentation, trial counts, timing, responses, and stop controls use the selected experiment settings.

Test output is saved in a **test_runs** subfolder of the selected results folder, using participant ID **TEST**, empty demographics, and a `test_mode` flag in the CSV. It does not report BioSemi recording confirmation or enabled serial hardware. Uncheck **Enable test mode** and save to restore the normal participant and recording workflow; the existing serial and Sophia Mode preferences are preserved. Test mode is off by default, including when older settings files are loaded. Its selection persists when saved.

## Recreate the environment on Windows

The repository is [zcm58/Necker-Studio](https://github.com/zcm58/Necker-Studio). Clone it, then run `powershell -ExecutionPolicy Bypass -File scripts/setup_environment.ps1` from the project folder. The bootstrap requires an existing Windows `py` launcher, downloads the pinned Python into `.python`, creates `.venv`, and installs `requirements.txt`. It does not install project packages globally. Select `.venv\Scripts\python.exe` as the PyCharm interpreter. The shared `.run` configuration points to that environment.

PsychoPy 2026.2.4 declares Python `>=3.10,<3.13`, so Python 3.12 is the newest supported series. The project uses its latest security release, 3.12.14. [PsychoPy metadata](https://pypi.org/project/psychopy/2026.2.4/) · [Python release](https://www.python.org/downloads/release/python-31214/)

The Windows `pyWinhook` dependency does not publish CPython 3.12 wheels on PyPI. This repository includes a wheel built by its Windows CI workflow from the published 1.6.2 source. A compiler alias maps the legacy `PyInt_AsLong` name to Python 3's `PyLong_AsLong`; the keyboard backend and experiment logic are retained. See `vendor/README.md` for the build and checksum. A compiler is not required on the experiment computer. The repository also includes Pyglet 1.4.11 with a one-line Windows font-buffer type correction for Python 3.12. Both compatibility changes are documented and reproducible; the original experiment routines are unchanged.

`requirements.in` lists the direct dependencies; `requirements.txt` pins the complete installed environment. Keep `assets`, `reference`, `vendor`, and `defaults.json` with the application. Virtual environments are machine-local and should be recreated after cloning or moving the project. Custom external stimulus paths must remain accessible on the destination computer.

## Settings

Settings are edited through the interface and saved automatically when **Save settings** is pressed. Cancel leaves the previous configuration intact. **Restore defaults** stages the original values; press Save to apply them. No Python, JSON, or spreadsheet editing is required.

The results folder persists across launches in the project's local `settings.json`, independently of PyCharm's working directory. Existing saved settings gain Sophia Mode without resetting the results folder, calibration, or protocol values. Settings use a section selector, wrapping labels, scrolling pages, and a fixed action area so controls remain accessible at smaller window sizes and larger text sizes. COM3 is greyed out and cannot be edited.

| Section | Controls |
| --- | --- |
| General | PsychoPy interpreter, output directory, test mode, Sophia Mode |
| Display | Full screen, display number, pixel dimensions, monitor calibration, cube size in degrees |
| Audio & triggers | Volume, serial enable/disable, locked COM3 port, baud rate |
| Trial counts | Practice, baseline, conditioning, final-measurement blocks/repetitions and demonstrations |
| Timing | Exposure, routine/response durations, fixation, blank-frame bounds, tone duration |
| Conditions | Edit, add, duplicate, remove, reorder, and browse stimuli for condition rows |

The demonstration table retains exactly four rows because the reference uses the first three for no-go demonstrations and the fourth for go demonstrations. Some original columns are metadata only: `LorR.image` and `ISI` do not drive the displayed cube or timing; that cube remains the bundled `Necker6.png`. `SoundA.correct` and `GoNoGo` are retained in the data but the reference does not calculate accuracy from them.

Stimuli are specified in visual degrees. By default the app uses the existing `testMonitor` calibration. If it is missing or incomplete, choose a calibrated monitor profile or enter the measured monitor width, viewing distance, and display pixel dimensions in Settings. Calibration overrides apply to this app's sessions without changing the saved PsychoPy monitor profile.

Serial triggers are enabled by default on **COM3 at 115200 baud**, matching the source. Disable them explicitly for sessions without the trigger device. Another program can still prevent access by holding the port; the app reports that case with instructions to close the other program and check the connection. The port is fixed to COM3 in both the interface and settings validation.

## Default protocol

Operator windows open with horizontal and vertical margins inside the active monitor's work area, including space for the title bar and taskbar. Settings pages remain scrollable.

| Phase | Trials |
| --- | ---: |
| Practice | 8 |
| Initial measurement | 120: 5 blocks × 3 repetitions × 8 conditions |
| Conditioning | 120: 5 blocks × 4 repetitions × 6 conditions |
| Final measurement | 120: 5 blocks × 3 repetitions × 8 conditions |
| Total | 368, plus 3 no-go and 2 go demonstrations |

The original instruction wording, pictures, WAV files, randomization methods, space/arrow keys, response windows, screen colors, breaks, and data field names are retained. Instruction text and illustrations fit within 5% horizontal and vertical margins using the actual display size. The intro and recap pages keep a gap between text and illustration. Choice and demonstration images shrink only if needed to fit. Experimental trial cubes retain the selected size in visual degrees and central position; invalid calibration or a cube larger than the safe area produces an error before trials begin. Layout is calculated before the experiment clock starts. Every block still ends with the original space-confirmed break, including the last block. Escape stops the experiment; the operator interface also provides **Stop session** and waits for the child process to save and close.

Fidelity details intentionally preserved:

- Only practice uses the silent `NeckerBaseline` routine. Both main measurement phases use the condition sounds.
- The blank interval tests `randint(62,125)` again each frame. It is not a single uniform duration sampled at trial onset.
- Choice responses retain queued arrow-key events, as configured by the source.
- Conditioning has two separate space-response windows, both of which can end early. Both response fields remain in the data.
- The existing trigger bytes and locations are retained: bytes 1 and 2 during initialization and byte 1 at practice-cube onset. The disabled trigger code remains disabled. This build does not silently move trigger writes to phase boundaries or frame flips.

## Repairs and compatibility

The supplied error log fails at the **second open of COM3**. The original generated script opens the same exclusive port twice. This app owns one connection and reuses it for both calls, then closes it on completion, Escape, operator stop, or failure. Repeated close requests are harmless. A regression test uses a fake exclusive serial port that would fail on a second open.

The installed runtime also exposed an audio preference compatibility issue: its preference is an ordered list, while the newer generated script assigns that list to a backend name. The adapter accepts both formats and selects the first registered backend in the preference order. It does not change the user's PsychoPy preferences.

The app runs a bundled, checksum-checked Python export instead of asking Builder to interpret the `.psyexp` XML, so the obsolete eye-tracker parameter warnings in the supplied log do not occur through Builder loading. The reference `.psyexp` is included for provenance only.

## Results

Each run gets a unique directory inside the selected output folder. By default this is `data/session_<participant>_<timestamp>/`.

- `data/`: original PsychoPy wide CSV, `.psydat`, and `.log` outputs.
- `session.json`: the exact settings and condition rows used, participant metadata, BioSemi operator confirmation, and selected interpreter.
- `runner.log`: startup and runtime diagnostics.
- `result.json`: completion/abort/failure status and data filename.

The **Open output folder** and **View run log** buttons provide access. A stop or runtime error attempts to save all data collected so far. The participant number, age, sex, and handedness retain their original Necker column names; colorblind status, removed electrodes, and recording confirmation are additional metadata. Existing participant data in the original project is untouched.

## Verification and maintenance

Run the automated tests with `python -m unittest discover -s tests -v` from this folder. The tests do not require PsychoPy, a display, or serial hardware. They cover the protocol, condition fixtures, timing changes, response semantics, saved settings, invalid settings, output isolation, audio compatibility, and the exclusive-port regression.

Twelve additional Tk interface tests are opt-in: set `NECKER_GUI_SMOKE=1` in the test run's environment. They briefly open windows but never launch an experiment or contact hardware. All **65 tests**, including these interface tests, passed on the development machine. Coverage includes saved-folder migration, locked COM3, required demographics, fresh typed recording confirmation, cancellation, settings at minimum size and with larger text, test-mode hardware suppression, separate test output, installed paths, screen margins, and restoration of normal launch checks. The generated stimulus source is identical when only test mode is toggled.

A full-screen test-mode session completed all 30 accelerated trials and four demonstrations with serial access explicitly blocked. Its CSV rows correctly identify the TEST participant, test mode, disabled serial hardware, and absent recording confirmation.

Validation on **Python 3.12.14 with PsychoPy 2026.2.4** included a complete accelerated 30-trial session plus four demonstrations with simulated responses. All phases completed, outputs were saved, and the process exited successfully. Earlier validation also included the Tk settings/run-state interface and a real PsychoPy startup with cooperative abort and saved data. The complete session produced CSV, psydat, and log files and reached the thanks screen. Test output is separate from participant output. The revised layout was checked at 1920×1080 full screen, 1280×720 and 800×600 using a 53 cm monitor width and 80 cm viewing distance: all instruction bounds fit within the margins, paired text/artwork do not overlap, and trial cube geometry is unchanged. Physical COM3 trigger delivery and laboratory audiovisual timing have not been measured.

`reference/experiment_source.py` is the unchanged September 29, 2026 generated script (PsychoPy 2026.2.3). `adapter.py` makes explicit, checked substitutions for settings and application integration while retaining the original frame loops. Replacing the reference requires reviewing the adapter and tests; its checksum deliberately rejects unreviewed changes.

## Build the Windows installer

With a clean committed checkout, the verified project environment and Inno Setup 6 installed, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_installer.ps1
```

This builds a native windowed launcher, copies the local CPython runtime and pinned site-packages into a relocatable bundle, verifies imports and dependencies, then compiles `packaging/necker.iss`. It does not install or update global packages. Output is the versioned x64 installer, SHA256SUMS.txt and release.json in `dist`. The bundle contains application source and dependency license files; it excludes saved settings, participant data and personal interpreter paths.

Use `-BundleOnly` to inspect and test a bundle before compiling, then `-ExistingBundle <path>` to compile that verified bundle. `-Iscc <path>` selects a different installed Inno Setup compiler.

Opt-in desktop checks:

```powershell
.venv\Scripts\python.exe scripts/verify_presentation.py
.venv\Scripts\python.exe scripts/verify_session.py --output .verification/new-session-check
```

The first checks real rendered bounds and captures every instruction page at three sizes using a 53 cm screen width and 80 cm viewing distance. The second runs the full phase sequence with shortened timings, simulated responses and blocked serial hardware. These are functional checks; they do not measure acquisition hardware timing.
