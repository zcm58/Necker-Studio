# Nicholas's Nice Necker Cube Experiment

A standalone operator interface for `__NEW_NECKER.psyexp`, with a File > Settings dialog and an FPVS Studio inspired light interface. PsychoPy still performs stimulus presentation, audio, response collection, and timing. Builder is not needed to run or configure a session.

## Windows release 1.1

Download the x64 installer from [GitHub Releases](https://github.com/zcm58/Necker-Studio/releases/tag/v1.1).
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

The File > Settings dialog configures the experiment. No source, JSON, or spreadsheet edits are required. Serial is enabled on COM3 by default and the port is locked. Normal runs require serial output; use **Enable test mode** for a session without BioSemi hardware.

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

Serial triggers are enabled by default on **COM3 at 115200 baud**, matching the source. Normal runs reject disabled serial output; only explicit test mode permits log-only markers. Another program can still prevent access by holding the port; the app reports that case with instructions to close the other program and check the connection. The port is fixed to COM3 in both the interface and settings validation.

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
- The existing trigger bytes and call locations are retained: bytes 1 and 2 during initialization, then byte 1 at each practice routine's start (before its first flip). The original source has no per-trial marker writes in the main measurement or conditioning phases. Markers remain at these original locations, rather than adopting FPVS's distinct frame-locked event schedule.

## Repairs and compatibility

Version 1.1 adds the applicable BioSemi safeguards from FPVS Studio (reference commit `be06531f828663030246a4be3b2bfa588b7bb2ba`, `triggers/serial_backend.py`, `runtime/triggers.py`, and `runtime/recording.py`):

| Protection | Necker regression coverage |
| --- | --- |
| Normal runs require serial output; only a boolean test-mode flag permits null output | `test_triggers.py`, `test_trigger_worker.py`, `test_gui.py` |
| COM3 opens once, before presentation, with explicit 8N1, nonblocking writes and flow control off | `test_triggers.py`, `test_fidelity.py` |
| Codes 1–255 use exactly one raw byte; zero, invalid codes and UTF-8 multi-byte payloads are rejected | `test_triggers.py` (all 255 valid values) |
| No automatic reset, flush, delay, retry, alternate port or fallback after failure | `test_triggers.py` |
| Missing dependencies, failed opens, disconnected ports and short/extra writes fail clearly | `test_triggers.py`, `test_trigger_worker.py` |
| Successful writes, explicit test skips and errors are distinguished in exported records | `test_triggers.py`, `test_trigger_worker.py` |
| Missing, extra, reordered or suppressed marker calls cannot report a completed session | source-site guard in `adapter.py`, completion audit in `triggers.py`, both tested |
| Failure preserves collected data, logs the error and closes the port | `test_trigger_worker.py` |

Every run exports `trigger_log.csv`; `result.json` includes trigger counts and transport identity. `sent` means the serial API accepted one byte, not proof of BioSemi acquisition. The log clock is seconds since connection construction, not a frame-onset timestamp. No log file IO occurs during stimulus presentation. A normal completed run must match the original schedule: two initialization markers plus one per practice trial. Aborted runs retain their partial audit without being treated as completed.

The bundle build runs all non-GUI regression tests before packaging and probes the checked transport inside the packaged interpreter. These checks use fake serial devices and never send codes to acquisition hardware. Physical cable/status-channel receipt still needs a BioSemi recording check.

The supplied error log fails at the **second open of COM3**. The original generated script opens the same exclusive port twice. This app owns one connection and reuses it for both calls, then closes it on completion, Escape, operator stop, or failure. Repeated close requests are harmless. A regression test uses a fake exclusive serial port that would fail on a second open.

The installed runtime also exposed an audio preference compatibility issue: its preference is an ordered list, while the newer generated script assigns that list to a backend name. The adapter accepts both formats and selects the first registered backend in the preference order. It does not change the user's PsychoPy preferences.

The app runs a bundled, checksum-checked Python export instead of asking Builder to interpret the `.psyexp` XML, so the obsolete eye-tracker parameter warnings in the supplied log do not occur through Builder loading. The reference `.psyexp` is included for provenance only.

## Results

Each run gets a unique directory inside the selected output folder. By default this is `data/session_<participant>_<timestamp>/`.

- `data/`: original PsychoPy wide CSV, `.psydat`, and `.log` outputs.
- `session.json`: the exact settings and condition rows used, participant metadata, BioSemi operator confirmation, and selected interpreter.
- `runner.log`: startup and runtime diagnostics.
- `result.json`: completion/abort/failure status and data filename.
- `trigger_log.csv`: each marker's code, call-site label, time, transport, sent/skipped/error status and error message.

The **Open output folder** and **View run log** buttons provide access. A stop or runtime error attempts to save all data collected so far. The participant number, age, sex, and handedness retain their original Necker column names; colorblind status, removed electrodes, and recording confirmation are additional metadata. Existing participant data in the original project is untouched.

## Verification and maintenance

Run the automated tests with `python -m unittest discover -s tests -v` from this folder. The tests do not require PsychoPy, a display, or serial hardware. They cover the protocol, condition fixtures, timing changes, response semantics, saved settings, invalid settings, output isolation, audio compatibility, and the exclusive-port regression.

Sixteen additional Tk interface tests are opt-in: set `NECKER_GUI_SMOKE=1` in the test run's environment. They briefly open windows but never launch an experiment or contact hardware. All **107 tests**, including these interface tests, passed on the development machine. Coverage includes saved-folder migration, locked COM3, required demographics, fresh typed recording confirmation, cancellation, settings at minimum size and with larger text, test-mode hardware suppression, separate test output, installed paths, screen margins, and restoration of normal launch checks. The generated stimulus source is identical when only test mode is toggled.

A full-screen test-mode session completed all 30 accelerated trials and four demonstrations with serial access explicitly blocked. Its CSV rows correctly identify the TEST participant, test mode, disabled serial hardware, and absent recording confirmation.

Validation on **Python 3.12.14 with PsychoPy 2026.2.4** included a complete accelerated 30-trial session plus four demonstrations with simulated responses. All phases completed, outputs were saved, and the process exited successfully. Earlier validation also included the Tk settings/run-state interface and a real PsychoPy startup with cooperative abort and saved data. The complete session produced CSV, psydat, and log files and reached the thanks screen. Test output is separate from participant output. The revised layout was checked at 1920×1080 full screen, 1280×720 and 800×600 using a 53 cm monitor width and 80 cm viewing distance: all instruction bounds fit within the margins, paired text/artwork do not overlap, and trial cube geometry is unchanged. Physical COM3 trigger delivery and laboratory audiovisual timing have not been measured.

`reference/experiment_source.py` is the unchanged September 29, 2026 generated script (PsychoPy 2026.2.3). `adapter.py` makes explicit, checked substitutions for settings and application integration while retaining the original frame loops. Replacing the reference requires reviewing the adapter and tests; its checksum deliberately rejects unreviewed changes.

## Automatic updates and smaller installers

Version 1.2 follows FPVS Studio's update workflow with a small native helper, adapted
for this Tk/Python application. Installed copies check the public GitHub releases in
the background at startup. **File > Check for updates** checks manually; **File >
Settings > Updates** controls startup checks. Checks do not download or install
anything automatically. Download the offered package, then choose **Install update**
and confirm. The application closes, setup runs, and the helper restarts the installed
application only after success. Updates cannot be installed during an experiment.
PyCharm source checkouts are never overwritten by the installer workflow.

Routine releases offer a direct patch for a specific previous version. The updater
verifies GitHub's release/asset identity, size and SHA-256, including the patch metadata.
It selects a patch only when the registered version and installed inventory match;
otherwise the full installer remains available. Patch discovery is quick and does not
scan the entire runtime. Native setup verifies the full baseline before changes and
checks the complete target afterward. A durable marker allows retrying a recognized
interrupted patch; unknown/corrupt states require the full installer. Failed target
verification returns exit code 12 and prevents automatic restart.

Patches replace changed application files without downloading or rewriting unchanged
Python/PsychoPy packages. Full installers also skip files whose SHA-256 already matches,
with separate compression blocks for the runtime and application. First installs still
include the complete pinned environment. Removing a runtime dependency simply to reduce
size could change the experiment's behavior; the runtime is retained intact.

The shared installer identity preserves settings and results. Update preferences are
stored separately in `updates.json` in the user state directory. Downloads are held in
`%LOCALAPPDATA%/NicholasNiceNeckerCubeExperiment/updates`, with a cross-process lock,
one recognized cached installer, cancellation cleanup and a staged helper. Unknown
files and directories are not recursively deleted. The repository is public and no
GitHub token is needed. Offline startup failures stay quiet; a manual check reports them.

## Build the Windows installer

With a clean committed checkout, the verified project environment and Inno Setup 6 installed, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_installer.ps1
```

This builds a native windowed launcher, copies the local CPython runtime and pinned site-packages into a relocatable bundle, verifies imports and dependencies, then compiles `packaging/necker.iss`. It does not install or update global packages. Output includes the versioned x64 installer, update JSON, SHA256SUMS.txt and release.json in `dist`. The bundle contains application source and dependency license files; it excludes saved settings, participant data and personal interpreter paths.

Use `-BundleOnly` to inspect and test a bundle before compiling, then `-ExistingBundle <path>` to compile that verified bundle. `-Iscc <path>` selects a different installed Inno Setup compiler.

Opt-in desktop checks:

```powershell
.venv\Scripts\python.exe scripts/verify_presentation.py
.venv\Scripts\python.exe scripts/verify_session.py --output .verification/new-session-check
```

The first checks real rendered bounds and captures every instruction page at three sizes using a 53 cm screen width and 80 cm viewing distance. The second runs the full phase sequence with shortened timings, simulated responses and blocked serial hardware. These are functional checks; they do not measure acquisition hardware timing.

For a direct patch, supply the exact retained published bundle and its authenticated
inventory digest. Never rebuild an old tag to invent a baseline:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_installer.ps1 -BaselineBundle <published-bundle> -BaselineManifestSha256 <sha256>
```

The target bundle must be committed and verified. The native setup verifier uses
Windows/.NET and does not depend on the installed Python. A patch cannot remove or
rename files; a release with such changes uses its full installer. Publish the full
installer, patch, versioned update JSON, checksum and release/validation reports together.
Keep release descriptions short. Never replace published installers under an old version.

Run `scripts/verify_patch_lifecycle.py` for isolated native acceptance. It uses a unique
fixture registration, no shortcuts, no app launch and no acquisition hardware. It covers
fresh installs, corrupted baselines, interrupted-patch recovery, wrong source versions,
unchanged-runtime preservation, full repair, failure exit codes and uninstall. Fixture
reports remain under ignored `build/` folders for review.
