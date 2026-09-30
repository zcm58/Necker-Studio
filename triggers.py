"""Checked BioSemi serial output; test mode is the only log-only transport.

Keep each write to one byte with no retry, reset, sleep or flush. Log primitive
attempts in memory, then export after presentation, as in FPVS Studio.
"""
from __future__ import annotations

import csv
import time


class TriggerError(RuntimeError):
    """Trigger output failed; the session must not report successful recording."""


def require_trigger_output(config):
    for key in ('serial_enabled', 'test_mode'):
        if type(config.get(key)) is not bool:
            raise ValueError(f'{key} must be a boolean.')
    if config.get('serial_port') != 'COM3':
        raise ValueError('Serial port is locked to COM3 for this experiment.')
    if not config['test_mode'] and not config['serial_enabled']:
        raise ValueError('BioSemi serial triggers are required for normal runs. Enable serial '
                         'triggers in File > Settings, or enable test mode for a hardware-free run.')


def validate_code(code):
    if type(code) is not int or not 1 <= code <= 255:
        raise ValueError('Trigger code must be an integer from 1 to 255; zero is reserved for reset.')
    return code


class SerialConnection:
    """Own one physical handle and return a checked writer to the Builder export."""

    def __init__(self, config, factory=None):
        require_trigger_output(config)
        self.config = dict(config)
        self.factory = factory
        self.handle = None
        self._opened = False
        self.records = []
        self._origin = time.monotonic()

    @property
    def backend_name(self):
        return 'null' if self.config['test_mode'] else 'serial'

    @property
    def emits_hardware_triggers(self):
        return self.backend_name == 'serial'

    def open(self):
        require_trigger_output(self.config)
        if self._opened:
            return self
        if self.config['test_mode']:
            self._opened = True
            return self
        factory = self.factory
        if factory is None:
            try:
                import serial
            except ImportError as exc:
                raise TriggerError('pyserial is required for BioSemi trigger output but is unavailable.') from exc
            factory = serial.Serial
        try:
            handle = factory(port='COM3', baudrate=self.config['serial_baud'],
                             bytesize=8, parity='N', stopbits=1, timeout=0, write_timeout=0,
                             rtscts=False, dsrdtr=False, xonxoff=False)
            if handle is None or not callable(getattr(handle, 'write', None)):
                raise TypeError('Serial backend did not return a writable connection.')
            if getattr(handle, 'is_open', True) is False:
                raise OSError('Serial backend returned a closed connection.')
        except Exception as exc:
            raise TriggerError(f'Could not open COM3 for BioSemi: {exc}\n'
                               'Check the trigger interface and close other programs using COM3. '
                               'Use File > Settings > Enable test mode only for a hardware-free run.') from exc
        self.handle = handle
        self._opened = True
        return self

    def write(self, payload):
        """Compatibility entry; reject text, multi-byte UTF-8 and reset payloads."""
        if not isinstance(payload, bytes) or len(payload) != 1:
            raise ValueError('A trigger write must contain exactly one raw byte.')
        return self.send(payload[0])

    def send(self, code, *, label='marker'):
        code = validate_code(code)
        stamp = time.monotonic() - self._origin
        status = 'sent'
        message = ''
        try:
            if not self._opened:
                raise TriggerError('BioSemi trigger connection is not open.')
            if self.config['test_mode']:
                status = 'skipped_disabled'
            else:
                if self.handle is None:
                    raise TriggerError('BioSemi serial backend is missing.')
                written = self.handle.write(bytes([code]))
                if type(written) is not int or written != 1:
                    raise TriggerError(f'Serial write returned {written!r}; expected exactly 1 byte.')
        except Exception as exc:
            message = f'Unable to send trigger code {code} on COM3: {exc}'
            self.records.append((stamp, code, label, 'error', message))
            raise TriggerError(message) from exc
        self.records.append((stamp, code, label, status, message))
        return 1

    def validate_completion(self, practice_count):
        """Detect missing, extra, reordered or silently suppressed original markers."""
        expected_status = 'skipped_disabled' if self.config['test_mode'] else 'sent'
        if len(self.records) != 2 + practice_count:
            raise TriggerError(f'Trigger audit failed: expected {2 + practice_count} marker attempts, '
                               f'recorded {len(self.records)}.')
        for index, (_, code, label, status, _) in enumerate(self.records):
            expected = ((1, 'initial_baseline') if index == 0 else
                        (2, 'initial_conditioned') if index == 1 else (1, 'practice_start'))
            if (code, label) != expected or status != expected_status:
                raise TriggerError(f'Trigger audit failed at marker {index + 1}: '
                                   f'{code}, {label}, {status}.')

    def summary(self):
        return {'backend': self.backend_name, 'attempted': len(self.records),
                **{s: sum(row[3] == s for row in self.records)
                   for s in ('sent', 'skipped_disabled', 'error')},
                'biosemi_receipt_verified': False}

    def export(self, path):
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(('trigger_index', 'time_since_connection_s', 'code', 'label',
                             'backend', 'status', 'message'))
            for index, (stamp, code, label, status, message) in enumerate(self.records):
                writer.writerow((index, stamp, code, label, self.backend_name, status, message))

    def close(self):
        handle, self.handle = self.handle, None
        self._opened = False
        if handle is not None:
            handle.close()
