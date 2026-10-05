from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


_SECRET_FRAGMENTS = ("token", "secret", "webhook", "password", "authorization", "api_key")


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): "<redacted>"
            if any(part in str(key).lower() for part in _SECRET_FRAGMENTS)
            else sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize(item) for item in value]
    return value


class AuditLogger:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path

    def record(
        self,
        *,
        tool: str,
        method: str,
        operation: str,
        params: dict[str, Any],
        result: str,
        error: str | None = None,
        confirmation_id: str | None = None,
        recipe_id: str | None = None,
    ) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "tool": tool,
            "method": method,
            "operation": operation,
            "params": sanitize(params),
            "result": result,
            "error": error,
            "confirmation_id": confirmation_id,
            "recipe_id": recipe_id,
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
