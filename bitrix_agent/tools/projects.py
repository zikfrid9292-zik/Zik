from __future__ import annotations

from typing import Any

from bitrix_agent.core.bitrix_client import BitrixClient


def find_projects(client: BitrixClient, name: str) -> Any:
    return client.call_read(
        "socialnetwork.api.workgroup.list",
        {
            "filter": {"=NAME": name, "=PROJECT": "Y"},
            "select": [
                "ID",
                "NAME",
                "PROJECT",
                "ACTIVE",
                "CLOSED",
                "PROJECT_DATE_START",
                "PROJECT_DATE_FINISH",
            ],
        },
    )
