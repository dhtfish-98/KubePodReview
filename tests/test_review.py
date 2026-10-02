import json
import unittest
from review import review_text


class KubeTests(unittest.TestCase):
    def test_missing_declarations(self):
        pod = {"kind": "Pod", "spec": {"containers": [{"name": "app", "securityContext": {"privileged": True}}]}}
        self.assertEqual(len(review_text(json.dumps(pod))), 5)

    def test_hardened_deployment(self):
        container = {"name": "app", "securityContext": {"allowPrivilegeEscalation": False, "readOnlyRootFilesystem": True, "capabilities": {"drop": ["ALL"]}}}
        obj = {"kind": "Deployment", "spec": {"template": {"spec": {"securityContext": {"runAsNonRoot": True}, "containers": [container]}}}}
        self.assertEqual(review_text(json.dumps(obj)), [])

    def test_invalid_schema(self):
        for value in ("{}", '{"kind":"Pod","spec":{"containers":[null]}}', "bad"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                review_text(value)
