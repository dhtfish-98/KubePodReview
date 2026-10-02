import json
import plistlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from review import review_text


class RegressionTests(unittest.TestCase):

    def test_types_root_and_added_capabilities(self):
        hardened={"allowPrivilegeEscalation":False,"readOnlyRootFilesystem":True,"runAsNonRoot":True,"capabilities":{"drop":["ALL"]}}
        pod={"kind":"Pod","spec":{"containers":[{"securityContext":dict(hardened,privileged="true")}]}}
        with self.assertRaises(ValueError): review_text(json.dumps(pod))
        pod["spec"]["containers"][0]["securityContext"]=dict(hardened,runAsUser=0,capabilities={"drop":["ALL"],"add":["SYS_ADMIN"]})
        self.assertEqual({x["rule"] for x in review_text(json.dumps(pod))},{"root-uid","added-capabilities"})
    def test_init_and_ephemeral_containers_are_reviewed(self):
        pod={"kind":"Pod","spec":{"containers":[{"name":"app"}],"initContainers":[{"name":"init","securityContext":{"privileged":True}}],"ephemeralContainers":[{"name":"debug"}]}}
        locations={x["location"] for x in review_text(json.dumps(pod))}
        self.assertEqual(locations,{"root.containers[0]","root.initContainers[0]","root.ephemeralContainers[0]"})
    def test_cronjob_nested_workload(self):
        cron={"kind":"CronJob","spec":{"jobTemplate":{"spec":{"template":{"spec":{"containers":[{"name":"job"}]}}}}}}
        self.assertEqual(len(review_text(json.dumps(cron))),4)
