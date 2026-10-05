from __future__ import annotations

from typing import Any

from bitrix_agent.core.bitrix_client import BitrixClient


TASK_SELECT = [
    "ID",
    "TITLE",
    "GROUP_ID",
    "PARENT_ID",
    "START_DATE_PLAN",
    "END_DATE_PLAN",
    "DEADLINE",
    "DURATION_PLAN",
    "DURATION_TYPE",
    "MATCH_WORK_TIME",
]


def find_tasks(client: BitrixClient, title: str, group_id: str | None = None) -> Any:
    filters: dict[str, Any] = {"TITLE": title}
    if group_id:
        filters["GROUP_ID"] = group_id
    return client.call_read("tasks.task.list", {"filter": filters, "select": TASK_SELECT})


def fields(client: BitrixClient) -> Any:
    return client.call_read("tasks.task.getFields")


def template_fields(client: BitrixClient) -> Any:
    return client.call_read("tasks.template.fields")


def templates(client: BitrixClient) -> Any:
    return client.call_read(
        "tasks.template.list", {"select": ["ID", "TITLE", "GROUP_ID", "PARENT_ID"]}
    )
