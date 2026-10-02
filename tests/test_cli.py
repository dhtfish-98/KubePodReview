import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from cli import main


class CLITests(unittest.TestCase):
    def test_finding_json_and_invalid_path(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input"
            payload = '{"kind": "Pod", "spec": {"containers": [{"name": "x"}]}}'
            path.write_bytes(payload if isinstance(payload, bytes) else payload.encode())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([str(path), "--json"]), 1)
            self.assertTrue(json.loads(output.getvalue()))
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(path) + ".missing"]), 2)
