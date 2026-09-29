"""Rebuild PsychoPy's pinned Pyglet with its Windows BYTE buffer type fixed.

Run from any working directory with Python 3.12. The result is written to vendor/.
Only the font buffer allocation and distribution version/RECORD are changed.
"""
from __future__ import annotations

import base64
import csv
import hashlib
import io
from pathlib import Path
import urllib.request
import zipfile

SOURCE_URL = (
    "https://files.pythonhosted.org/packages/b2/de/"
    "55594ab6496d6c08f511531502b614271c3120617b7068ba9b98d4284f04/"
    "pyglet-1.4.11-py2.py3-none-any.whl"
)
SOURCE_SHA256 = "8a8317fbb2bae145bd80f6d92d66b6dbbc9d13f1cbbed682ff55793a63003a46"
VERSION = "1.4.11+necker1"


def build(destination: Path) -> Path:
    with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
        source = response.read()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("Upstream wheel checksum differs; no wheel was built")
    old_info = "pyglet-1.4.11.dist-info/"
    new_info = f"pyglet-{VERSION}.dist-info/"
    entries = {}
    with zipfile.ZipFile(io.BytesIO(source)) as archive:
        for member in archive.infolist():
            if member.is_dir() or member.filename == old_info + "RECORD":
                continue
            contents = archive.read(member)
            filename = member.filename.replace(old_info, new_info, 1)
            if filename == "pyglet/font/win32.py":
                before = b"self._data = (ctypes.c_byte * (4 * width * height))()"
                after = b"self._data = (BYTE * (4 * width * height))()"
                if contents.count(before) != 1:
                    raise ValueError("The expected upstream allocation was not found")
                contents = contents.replace(before, after)
            elif filename == new_info + "METADATA":
                contents = contents.replace(b"Version: 1.4.11\n", f"Version: {VERSION}\n".encode(), 1)
            entries[filename] = contents

    record = io.StringIO(newline="")
    writer = csv.writer(record, lineterminator="\n")
    for filename, contents in sorted(entries.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(contents).digest()).rstrip(b"=").decode()
        writer.writerow([filename, "sha256=" + digest, len(contents)])
    writer.writerow([new_info + "RECORD", "", ""])
    entries[new_info + "RECORD"] = record.getvalue().encode()
    destination.mkdir(parents=True, exist_ok=True)
    result = destination / f"pyglet-{VERSION}-py2.py3-none-any.whl"
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename, contents in sorted(entries.items()):
            member = zipfile.ZipInfo(filename, date_time=(2026, 9, 29, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            member.external_attr = 0o644 << 16
            archive.writestr(member, contents)
    print(f"{result.name}  SHA256={hashlib.sha256(result.read_bytes()).hexdigest()}")
    return result


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1] / "vendor")
