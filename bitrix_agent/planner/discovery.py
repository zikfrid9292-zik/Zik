from __future__ import annotations

from typing import Any, Callable

from bitrix_agent.core.bitrix_client import BitrixClient, BitrixError
from bitrix_agent.memory.database import Memory
from bitrix_agent.tools import bizproc, projects, tasks


CANDIDATE_METHODS = (
    "socialnetwork.api.workgroup.list",
    "tasks.task.list",
    "tasks.task.get",
    "tasks.task.getfields",
    "tasks.task.gantt.link.list",
    "tasks.template.list",
    "tasks.template.get",
    "tasks.template.fields",
    "task.dependence.add",
    "task.dependence.delete",
    "bizproc.workflow.template.list",
)


class TestProjectDiscovery:
    def __init__(self, client: BitrixClient, memory: Memory) -> None:
        self.client = client
        self.memory = memory

    def run(self) -> dict[str, Any]:
        report: dict[str, Any] = {"methods": {}}
        report["scopes"] = self._probe(
            "portal scopes", "scope", {}, lambda: self.client.call_read("scope")
        )
        for method in CANDIDATE_METHODS:
            availability = self._probe(
                f"availability of {method}",
                "method.get",
                {"name": method.lower()},
                lambda method=method: self.client.call_read("method.get", {"name": method.lower()}),
            )
            report["methods"][method] = availability
            self.memory.map_item("rest_method", method, method, availability)

        report["projects"] = self._probe(
            "find project Test",
            "socialnetwork.api.workgroup.list",
            {"name": "Test"},
            lambda: projects.find_projects(self.client, "Test"),
        )
        project_id = _single_project_id(report["projects"])
        report["tasks"] = self._probe(
            "find task Test",
            "tasks.task.list",
            {"title": "Test", "group_id": project_id},
            lambda: tasks.find_tasks(self.client, "Test", project_id),
        )
        report["task_fields"] = self._probe(
            "inspect task fields", "tasks.task.getFields", {}, lambda: tasks.fields(self.client)
        )
        report["template_fields"] = self._probe(
            "inspect task template fields",
            "tasks.template.fields",
            {},
            lambda: tasks.template_fields(self.client),
        )
        if _available(report["methods"].get("tasks.template.list")):
            report["task_templates"] = self._probe(
                "list task templates",
                "tasks.template.list",
                {},
                lambda: tasks.templates(self.client),
            )
        else:
            report["task_templates"] = {"status": "unavailable"}
        if _available(report["methods"].get("bizproc.workflow.template.list")):
            report["bizproc_templates"] = self._probe(
                "list workflow templates",
                "bizproc.workflow.template.list",
                {},
                lambda: bizproc.templates(self.client),
            )
        else:
            report["bizproc_templates"] = {"status": "unavailable"}

        for kind in (
            "projects",
            "tasks",
            "task_fields",
            "template_fields",
            "task_templates",
            "bizproc_templates",
        ):
            self.memory.map_item(
                kind, "", "Test" if kind in {"projects", "tasks"} else "", report[kind]
            )
        return report

    def _probe(
        self, goal: str, method: str, params: dict[str, Any], call: Callable[[], Any]
    ) -> Any:
        try:
            result = call()
        except BitrixError as exc:
            error = str(exc)
            self.memory.experiment(goal, method, params, error=error, success=False)
            return {"status": "error", "error": error}
        self.memory.experiment(goal, method, params, result=result, success=True)
        return result


def _available(value: Any) -> bool:
    return isinstance(value, dict) and bool(value.get("isAvailable"))


def _single_project_id(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    items = value.get("workgroups", [])
    return str(items[0]["id"]) if len(items) == 1 and "id" in items[0] else None
