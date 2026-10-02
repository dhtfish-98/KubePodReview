# KubePodReview

Review selected securityContext declarations in a local Kubernetes workload JSON object. It runs locally, does not contact targets, and reports review prompts instead of exploit instructions.

## Input and checks

- Input: Kubernetes JSON from a system you own or are authorized to inspect.
- Checks: Privileged mode, escalation, writable root, non-root and capability-drop declarations.
- Output: rule, local location and short note. No source snippets, credential values or log identities are printed.

## Run

```sh
python cli.py ./owned-input
python cli.py ./owned-input --json
python -m unittest discover -s tests -v
```

Exit code 0 means no findings, 1 means review findings, 2 means invalid input or read failure. A clean result is not a security guarantee. The input file is read through a bounded regular-file descriptor with a 4 MiB limit.

## Boundaries

JSON only; admission policies, image contents, runtime class and cluster-effective policy are not evaluated. Work only on local, authorized inputs. The analysis does not send data to a service or modify the inspected files.

## Source and policy context

- Technical reference: https://kubernetes.io/docs/concepts/security/pod-security-standards/
- See [ORIGIN.md](ORIGIN.md) for implementation provenance and [VALIDATION.md](VALIDATION.md) for checks performed.
- CVP eligibility depends on a real, legitimate defensive task affected by Claude's cyber safeguards and the applicant's organization/identity review; this repository alone does not establish eligibility or approval. [Anthropic CVP guidance](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet).

## Reviewed input behavior

Pod, Deployment, DaemonSet, StatefulSet, Job, CronJob and List JSON are supported. Regular, init and ephemeral containers are inspected. Invalid security-field types are errors; UID 0, added capabilities and host namespace requests are also review prompts. Cluster admission and runtime behavior remain unresolved.

JSON input rejects duplicate object keys and nonstandard numbers; container nesting is limited to 128 levels.
