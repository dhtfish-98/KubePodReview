# Validation record

Scope: Privileged mode, escalation, writable root, non-root and capability-drop declarations.

Local checks to rerun:

```sh
python -m unittest discover -s tests -v
python cli.py --help
python -m compileall -q review.py cli.py tests
```

Check the exact public GitHub commit and its workflow run separately after publishing. Tests use synthetic input; no production system or external target is exercised. JSON only; admission policies, inherited defaults, runtime class, sidecars and cluster-effective policy are not evaluated.

## Current source result (2026-10-02)

- Python 3.14.6: 9/9 unit and CLI integration tests passed.
- Tests include the specific malformed-input, incomplete-review and declaration cases added during the source audit.
- Pod, Deployment, DaemonSet, StatefulSet, Job, CronJob and List JSON are supported. Regular, init and ephemeral containers are inspected. Invalid security-field types are errors; UID 0, added capabilities and host namespace requests are also review prompts. Cluster admission and runtime behavior remain unresolved.
- Test input is synthetic. No external target, live credential or production cluster is exercised.
- The public commit and its corresponding GitHub workflow must be verified separately after this update.
