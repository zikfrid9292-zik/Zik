from __future__ import annotations

from typing import Any

from bitrix_agent.core.bitrix_client import BitrixClient


def templates(client: BitrixClient) -> Any:
    return client.call_read(
        "bizproc.workflow.template.list",
        {
            "select": [
                "ID",
                "NAME",
                "MODULE_ID",
                "ENTITY",
                "DOCUMENT_TYPE",
                "AUTO_EXECUTE",
                "SYSTEM_CODE",
            ]
        },
    )
