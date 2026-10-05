from __future__ import annotations

from enum import StrEnum


class Operation(StrEnum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    UNKNOWN = "UNKNOWN"


class SafetyViolation(RuntimeError):
    pass


_READ_METHODS = {
    "method.get",
    "methods",
    "scope",
    "profile",
    "server.time",
    "socialnetwork.api.workgroup.list",
    "sonet_group.get",
    "tasks.task.list",
    "tasks.task.get",
    "tasks.task.getfields",
    "tasks.task.gantt.link.list",
    "tasks.template.get",
    "tasks.template.fields",
    "tasks.template.list",
    "task.item.list",
    "bizproc.workflow.template.list",
}


def classify_method(method: str) -> Operation:
    normalized = method.strip().lower()
    if normalized in _READ_METHODS:
        return Operation.READ
    if normalized.endswith((".delete", ".remove")):
        return Operation.DELETE
    if normalized.endswith((".add", ".create", ".update", ".set", ".bind")):
        return Operation.WRITE
    return Operation.UNKNOWN


def require_read(method: str) -> None:
    operation = classify_method(method)
    if operation is not Operation.READ:
        raise SafetyViolation(f"Blocked non-READ or unknown Bitrix method: {method!r}")
