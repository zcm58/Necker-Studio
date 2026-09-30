"""BioSemi regression protection aligned with FPVS Studio's serial contracts."""
import csv
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapter import build_source, validate_trigger_sites
from settings import default_settings
from triggers import SerialConnection, TriggerError, require_trigger_output


class Port:
    def __init__(self, returned=1, error=None):
        self.returned, self.error = returned, error
        self.writes, self.close_calls = [], 0

    def write(self, value):
        self.writes.append(value)
        if self.error:
            raise self.error
        return self.returned

    def close(self):
        self.close_calls += 1


class TriggerTests(unittest.TestCase):
    def connection(self, **kwargs):
        port = Port(**kwargs)
        factory = Mock(return_value=port)
        connection = SerialConnection(default_settings(), factory=factory)
        connection.open()
        self.addCleanup(connection.close)
        return connection, port, factory

    def test_biosemi_8n1_nonblocking_no_flow_control_and_no_open_marker(self):
        connection, port, factory = self.connection()
        self.assertIs(connection.open(), connection)
        factory.assert_called_once_with(port='COM3', baudrate=115200, bytesize=8,
            parity='N', stopbits=1, timeout=0, write_timeout=0,
            rtscts=False, dsrdtr=False, xonxoff=False)
        self.assertEqual(port.writes, [])

    def test_all_valid_codes_are_exactly_one_raw_byte_without_reset_or_retry(self):
        connection, port, _ = self.connection()
        for code in range(1, 256):
            connection.send(code)
        self.assertEqual(port.writes, [bytes([code]) for code in range(1, 256)])
        self.assertEqual(connection.summary()['sent'], 255)
        self.assertFalse(connection.summary()['biosemi_receipt_verified'])

    def test_invalid_codes_never_reach_serial(self):
        connection, port, _ = self.connection()
        for code in (-1, 0, 256, None, '55', True, False, 1.0):
            with self.subTest(code=code), self.assertRaises(ValueError):
                connection.send(code)
        self.assertEqual(port.writes, [])

    def test_legacy_writer_rejects_utf8_multibyte_text_and_reset(self):
        connection, port, _ = self.connection()
        for payload in ('1', b'', b'\x00', chr(255).encode(), b'12'):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                connection.write(payload)
        connection.write(b'\xff')
        self.assertEqual(port.writes, [b'\xff'])

    def test_short_extra_and_unreported_writes_are_errors_not_sent(self):
        for returned in (0, 2, -1, None, True):
            with self.subTest(returned=returned):
                connection, port, _ = self.connection(returned=returned)
                with self.assertRaisesRegex(TriggerError, 'expected exactly 1 byte'):
                    connection.send(55, label='probe')
                self.assertEqual(port.writes, [b'7'])
                self.assertEqual(connection.summary()['sent'], 0)
                self.assertEqual(connection.summary()['error'], 1)

    def test_write_exception_is_logged_and_reraised_without_retry(self):
        connection, port, _ = self.connection(error=OSError('disconnected'))
        with self.assertRaisesRegex(TriggerError, 'disconnected'):
            connection.send(1)
        self.assertEqual(port.writes, [b'\x01'])
        self.assertEqual(connection.records[0][3], 'error')

    def test_open_failure_and_missing_pyserial_never_fall_back_to_null(self):
        factory = Mock(side_effect=OSError('busy'))
        connection = SerialConnection(default_settings(), factory=factory)
        with self.assertRaisesRegex(TriggerError, 'COM3'):
            connection.open()
        factory.assert_called_once()
        self.assertEqual(connection.backend_name, 'serial')
        self.assertIsNone(connection.handle)
        with patch.dict(sys.modules, {'serial': None}), self.assertRaisesRegex(TriggerError, 'pyserial'):
            SerialConnection(default_settings()).open()

    def test_missing_or_closed_connection_is_not_accepted_as_a_backend(self):
        for handle in (None, object(), Mock(is_open=False)):
            with self.subTest(handle=handle), self.assertRaises(TriggerError):
                SerialConnection(default_settings(), factory=Mock(return_value=handle)).open()

    def test_normal_run_cannot_disable_output_and_flags_must_be_booleans(self):
        config = default_settings()
        config['serial_enabled'] = False
        with self.assertRaisesRegex(ValueError, 'required for normal runs'):
            SerialConnection(config, factory=Mock())
        for key in ('test_mode', 'serial_enabled'):
            for value in (1, 0, 'true', 'false', None):
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    require_trigger_output({**default_settings(), key: value})

    def test_test_mode_is_explicitly_skipped_and_never_imports_or_opens_serial(self):
        for enabled in (True, False):
            config = {**default_settings(), 'test_mode': True, 'serial_enabled': enabled}
            factory = Mock(side_effect=AssertionError('hardware must not be touched'))
            with patch.dict(sys.modules, {'serial': None}):
                connection = SerialConnection(config, factory=factory)
                connection.open()
                connection.send(1, label='initial_baseline')
                connection.send(2, label='initial_conditioned')
                connection.validate_completion(0)
                connection.close()
            factory.assert_not_called()
            self.assertEqual(connection.summary()['sent'], 0)
            self.assertEqual(connection.summary()['skipped_disabled'], 2)
            self.assertFalse(connection.emits_hardware_triggers)

    def test_close_is_idempotent_and_writes_after_close_fail(self):
        connection, port, _ = self.connection()
        connection.close()
        connection.close()
        self.assertEqual(port.close_calls, 1)
        with self.assertRaises(TriggerError):
            connection.send(1)
        self.assertEqual(port.writes, [])

    def test_completion_audit_rejects_missing_extra_reordered_and_log_only_records(self):
        for variant in ('empty', 'missing', 'extra', 'order', 'null', 'code'):
            with self.subTest(variant=variant):
                connection, _, _ = self.connection()
                if variant != 'empty':
                    connection.send(1, label='initial_baseline')
                    connection.send(2, label='initial_conditioned')
                    connection.send(1, label='practice_start')
                    connection.validate_completion(1)
                if variant == 'missing':
                    connection.records.pop()
                elif variant == 'extra':
                    connection.send(1, label='practice_start')
                elif variant == 'order':
                    connection.records.reverse()
                elif variant in ('null', 'code'):
                    row = list(connection.records[0])
                    row[3 if variant == 'null' else 1] = 'skipped_disabled' if variant == 'null' else 3
                    connection.records[0] = tuple(row)
                with self.assertRaisesRegex(TriggerError, 'audit failed'):
                    connection.validate_completion(1)

    def test_trigger_log_distinguishes_real_write_success_and_failure(self):
        connection, port, _ = self.connection()
        connection.send(128, label='example')
        port.error = OSError('unplugged')
        with self.assertRaises(TriggerError):
            connection.send(255, label='example')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'trigger_log.csv'
            connection.export(path)
            with path.open(newline='') as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual([r['status'] for r in rows], ['sent', 'error'])
        self.assertEqual([r['code'] for r in rows], ['128', '255'])
        self.assertTrue(all(r['backend'] == 'serial' for r in rows))

    def test_source_guard_rejects_missing_marker_unchecked_write_and_moved_practice(self):
        source = build_source(default_settings())
        validate_trigger_sites(source)
        changes = [source.replace('send_trigger(2, label="initial_conditioned")', 'pass'),
                   source.replace('send_trigger(1, label="initial_baseline")', 'send_trigger(3, label="initial_baseline")'),
                   source.replace('send_trigger(1, label="practice_start")', 'port.write(b"x")')]
        for changed in changes:
            with self.assertRaises(RuntimeError):
                validate_trigger_sites(changed)


if __name__ == '__main__':
    unittest.main()
