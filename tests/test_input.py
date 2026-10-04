import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from local_input import read_local_file


class InputTests(unittest.TestCase):
    def test_stream_construction_failure_closes_descriptor(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input"
            path.write_bytes(b"synthetic")
            opened = []

            def fail_fdopen(descriptor, mode):
                opened.append(descriptor)
                raise OSError("stream creation failed")

            with patch("local_input.os.fdopen", side_effect=fail_fdopen):
                with self.assertRaisesRegex(OSError, "stream creation failed"):
                    read_local_file(path)

            self.assertEqual(len(opened), 1)
            descriptor = opened[0]
            try:
                with self.assertRaises(OSError) as error:
                    os.fstat(descriptor)
                self.assertEqual(error.exception.errno, errno.EBADF)
            finally:
                try:
                    os.close(descriptor)
                except OSError as error:
                    if error.errno != errno.EBADF:
                        raise

    def test_stream_construction_error_survives_a_closed_descriptor(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input"
            path.write_bytes(b"synthetic")

            def close_then_fail(descriptor, mode):
                os.close(descriptor)
                raise ValueError("stream setup failed after close")

            with patch("local_input.os.fdopen", side_effect=close_then_fail):
                with self.assertRaisesRegex(ValueError, "stream setup failed after close"):
                    read_local_file(path)

    def test_oversized_link_and_nonregular_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            path=root/"input"
            path.write_bytes(b"x"*9)
            with self.assertRaises(ValueError): read_local_file(path,8)
            link=root/"link"
            link.symlink_to(path)
            with self.assertRaises(ValueError): read_local_file(link)
            with self.assertRaises((ValueError,OSError)): read_local_file(root)
            if hasattr(os,"mkfifo"):
                pipe=root/"pipe"
                os.mkfifo(pipe)
                with self.assertRaises(ValueError): read_local_file(pipe)

    def test_ambiguous_and_deep_json_rejected(self):
        from strict_json import loads
        for value in ('{"setting":true,"setting":false}', '{"number":NaN}', '['*2000+'0'+']'*2000):
            with self.subTest(value=value[:40]),self.assertRaises(ValueError): loads(value)
