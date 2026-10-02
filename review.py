"""Read-only prompts for Kubernetes Pod JSON security declarations."""
from __future__ import annotations
from strict_json import loads


def _mapping(value, field):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _booleans(value, names):
    for name in names:
        if name in value and type(value[name]) is not bool:
            raise ValueError(f"{name} must be a boolean")


def _security(value):
    value = _mapping(value, "securityContext")
    _booleans(value, ("privileged", "allowPrivilegeEscalation", "readOnlyRootFilesystem", "runAsNonRoot"))
    if "runAsUser" in value and (type(value["runAsUser"]) is not int or value["runAsUser"] < 0):
        raise ValueError("runAsUser must be a nonnegative integer")
    return value


def _pod_specs(document, location="root"):
    if not isinstance(document, dict) or not isinstance(document.get("kind"), str):
        raise ValueError("expected a Kubernetes workload object")
    kind = document["kind"]
    if kind == "List":
        items = document.get("items")
        if not isinstance(items, list):
            raise ValueError("List.items must be an array")
        for index, item in enumerate(items):
            yield from _pod_specs(item, f"{location}.items[{index}]")
        return
    spec = _mapping(document.get("spec"), "spec")
    if kind in ("Deployment", "DaemonSet", "StatefulSet", "Job"):
        spec = _mapping(_mapping(spec.get("template"), "template").get("spec"), "template.spec")
    elif kind == "CronJob":
        job = _mapping(spec.get("jobTemplate"), "jobTemplate")
        job_spec = _mapping(job.get("spec"), "jobTemplate.spec")
        spec = _mapping(_mapping(job_spec.get("template"), "template").get("spec"), "template.spec")
    elif kind != "Pod":
        raise ValueError("unsupported workload kind")
    if not isinstance(spec.get("containers"), list) or not spec["containers"]:
        raise ValueError("Pod needs a nonempty containers array")
    yield location, spec


def review_text(text: str) -> list[dict[str, str]]:
    document = loads(text)
    findings = []
    try:
        pods = list(_pod_specs(document))
    except RecursionError as exc:
        raise ValueError("workload nesting is too deep") from exc
    for pod_location, spec in pods:
        pod_security = _security(spec.get("securityContext"))
        _booleans(spec, ("hostNetwork", "hostPID", "hostIPC"))
        for field in ("hostNetwork", "hostPID", "hostIPC"):
            if spec.get(field) is True:
                findings.append({"rule": "host-namespace", "location": f"{pod_location}.{field}", "note": "Pod requests a host namespace"})
        for group in ("containers", "initContainers", "ephemeralContainers"):
            containers = spec.get(group, [])
            if not isinstance(containers, list):
                raise ValueError(f"{group} must be an array")
            for index, container in enumerate(containers):
                if not isinstance(container, dict):
                    raise ValueError("container must be an object")
                location = f"{pod_location}.{group}[{index}]"
                security = _security(container.get("securityContext"))
                def add(rule, note):
                    findings.append({"rule": rule, "location": location, "note": note})
                if security.get("privileged") is True:
                    add("privileged", "Container requests privileged mode")
                if security.get("allowPrivilegeEscalation") is not False:
                    add("escalation-not-disabled", "Privilege escalation is not explicitly disabled")
                if security.get("readOnlyRootFilesystem") is not True:
                    add("writable-root", "Read-only root filesystem is not explicitly enabled")
                if security.get("runAsNonRoot", pod_security.get("runAsNonRoot")) is not True:
                    add("nonroot-not-declared", "Non-root execution is not explicitly declared")
                if security.get("runAsUser", pod_security.get("runAsUser")) == 0:
                    add("root-uid", "Container explicitly selects UID 0")
                capabilities = _mapping(security.get("capabilities"), "capabilities")
                for field in ("drop", "add"):
                    entries = capabilities.get(field, [])
                    if not isinstance(entries, list) or not all(isinstance(item, str) and item for item in entries):
                        raise ValueError("capability lists must contain strings")
                if "ALL" not in capabilities.get("drop", []):
                    add("capabilities-not-dropped", "All Linux capabilities are not explicitly dropped")
                if capabilities.get("add"):
                    add("added-capabilities", "Capabilities are explicitly added; review necessity")
    return findings
