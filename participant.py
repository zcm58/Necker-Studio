"""Launch-time participant validation shared by the dialog and runtime."""
from __future__ import annotations

import re

SEX_VALUES = ("Female", "Male")
HANDEDNESS_VALUES = ("Right handed", "Left handed", "Ambidextrous")
HANDEDNESS_KEY = "handedness (left or right)"


class ParticipantError(ValueError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(message)


def validate_participant(values: dict) -> dict:
    """Match FPVS's required fields, retaining the original Necker column names."""
    def text(key):
        value = values.get(key, "")
        return value.strip() if isinstance(value, str) else ""

    identifier = text("participant_ID")
    if not identifier or not identifier.isascii() or not identifier.isdigit():
        raise ParticipantError("participant_ID", "Participant number is required and must contain digits only (for example, 0012).")
    age = values.get("age", "")
    if isinstance(age, str):
        age = age.strip()
        if age.isascii() and age.isdigit() and len(age) <= 3:
            age = int(age)
    if type(age) is not int or not 1 <= age <= 120:
        raise ParticipantError("age", "Participant age must be a whole number from 1 to 120.")
    sex = text("sex")
    if sex not in SEX_VALUES:
        raise ParticipantError("sex", "Select the participant sex to launch the session.")
    handedness = text(HANDEDNESS_KEY)
    if handedness not in HANDEDNESS_VALUES:
        raise ParticipantError(HANDEDNESS_KEY, "Select the participant handedness to launch the session.")
    colorblind = values.get("colorblind")
    if type(colorblind) is not bool:
        raise ParticipantError("colorblind", "Select whether the participant is colorblind to launch the session.")
    # FPVS accepts comma, semicolon, or newline-separated labels, normalizes
    # case, removes bidi controls, and de-duplicates without guessing the cap.
    removed = values.get("manual_removed_electrodes", "")
    raw_labels = [removed] if isinstance(removed, str) else removed
    if not isinstance(raw_labels, (list, tuple)) or any(not isinstance(v, str) for v in raw_labels):
        raise ParticipantError("manual_removed_electrodes", "Manually removed electrode labels must be text.")
    labels = []
    bidi = dict.fromkeys(map(ord, "\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"))
    for raw in raw_labels:
        for label in re.split(r"[,;\r\n]+", raw):
            label = label.translate(bidi).strip().upper()
            if any(ord(character) < 32 for character in label):
                raise ParticipantError("manual_removed_electrodes", "Electrode labels cannot contain control characters.")
            if label and label not in labels:
                labels.append(label)
    return {"participant_ID": identifier, "age": age, "sex": sex,
            HANDEDNESS_KEY: handedness, "colorblind": colorblind,
            "manual_removed_electrodes": labels}


def session_participant(config: dict, values: dict | None) -> dict:
    """Use explicitly nonparticipant metadata for a hardware-free test run."""
    if config["test_mode"]:
        return {"participant_ID": "TEST", "age": None, "sex": None,
                HANDEDNESS_KEY: None, "colorblind": None, "manual_removed_electrodes": []}
    if not isinstance(values, dict):
        raise ParticipantError("participant_ID", "Participant details are required for a normal session.")
    return validate_participant(values)


def recording_confirmation_required(config: dict) -> bool:
    return config["sophia_mode"] and not config["test_mode"]


def require_recording_confirmation(config: dict, confirmed: bool) -> None:
    if recording_confirmation_required(config) and confirmed is not True:
        raise ValueError("Sophia Mode requires confirmation that the BioSemi PC is recording before launching.")
