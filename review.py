"""Read-only prompts for selected Kubernetes Pod JSON security settings."""

from __future__ import annotations

import json


def review_text(text: str) -> list[dict[str, str]]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid Kubernetes JSON") from exc
    if not isinstance(document, dict) or document.get("kind") not in ("Pod", "Deployment", "DaemonSet", "StatefulSet", "Job"):
        raise ValueError("expected a supported Kubernetes workload object")
    kind = document["kind"]
    spec = document.get("spec")
    if not isinstance(spec, dict):
        raise ValueError("missing spec")
    if kind in ("Deployment", "DaemonSet", "StatefulSet", "Job"):
        template = spec.get("template")
        spec = template.get("spec") if isinstance(template, dict) else None
    if not isinstance(spec, dict) or not isinstance(spec.get("containers"), list):
        raise ValueError("missing Pod containers")
    findings = []
    pod_security = spec.get("securityContext") or {}
    if not isinstance(pod_security, dict):
        raise ValueError("invalid Pod securityContext")
    for index, container in enumerate(spec["containers"]):
        if not isinstance(container, dict):
            raise ValueError("container must be an object")
        location = f"containers[{index}]"
        security = container.get("securityContext") or {}
        if not isinstance(security, dict):
            raise ValueError("invalid container securityContext")

        def add(rule: str, note: str) -> None:
            findings.append({"rule": rule, "location": location, "note": note})

        if security.get("privileged") is True:
            add("privileged", "Container requests privileged mode")
        if security.get("allowPrivilegeEscalation") is not False:
            add("escalation-not-disabled", "Privilege escalation is not explicitly disabled")
        if security.get("readOnlyRootFilesystem") is not True:
            add("writable-root", "Read-only root filesystem is not explicitly enabled")
        if security.get("runAsNonRoot", pod_security.get("runAsNonRoot")) is not True:
            add("nonroot-not-declared", "Non-root execution is not explicitly declared")
        capabilities = security.get("capabilities") or {}
        if not isinstance(capabilities, dict):
            raise ValueError("invalid capabilities")
        dropped = capabilities.get("drop") or []
        if not isinstance(dropped, list) or not all(isinstance(item, str) for item in dropped):
            raise ValueError("invalid dropped capabilities")
        if "ALL" not in dropped:
            add("capabilities-not-dropped", "All Linux capabilities are not explicitly dropped")
    return findings
