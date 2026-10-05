# v0.1.0 — 2026-10-05

First source-only release of KubePodReview.

Review selected securityContext declarations in a local Kubernetes workload JSON object. It runs locally, does not contact targets, and reports review prompts instead of exploit instructions.

This tag distributes the repository source through GitHub's automatic source archives. It does not include a wheel, executable, or other built package. The `构建.py --build` adapter for this project remains manual and does not produce a distribution.

The review operates on local, owner-supplied or otherwise authorized input. Its checks are deliberately narrow; tests use representative and synthetic cases. A successful test or a clean review result does not establish broad security coverage, a live finding, or CVP qualification. Application eligibility depends on the applicant's real defensive task and Anthropic's review.

See [README](README.md) for the exact checks, limits, and run commands; [VALIDATION](VALIDATION.md) for recorded checks; [ORIGIN](ORIGIN.md) and [LICENSE](LICENSE) for provenance and rights. External dependencies retain their own licenses.
