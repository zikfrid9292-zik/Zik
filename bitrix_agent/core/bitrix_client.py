from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .audit import AuditLogger
from .safety import require_read


class BitrixError(RuntimeError):
    pass


class BitrixClient:
    """Small webhook client whose public API can perform READ operations only."""

    def __init__(
        self, webhook_url: str, audit: AuditLogger | None = None, timeout: float = 30
    ) -> None:
        self.__webhook_url = webhook_url.rstrip("/")
        self.audit = audit or AuditLogger()
        self.timeout = timeout

    def call_read(self, method: str, params: dict[str, Any] | None = None) -> Any:
        require_read(method)
        safe_params = params or {}
        request = Request(
            f"{self.__webhook_url}/{method}.json",
            data=json.dumps(safe_params).encode("utf-8"),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            self.audit.record(
                tool="bitrix_client",
                method=method,
                operation="READ",
                params=safe_params,
                result="failure",
                error=type(exc).__name__,
            )
            raise BitrixError(f"Bitrix READ request failed for {method}") from None
        if "error" in payload:
            code = str(payload.get("error", "unknown_error"))
            self.audit.record(
                tool="bitrix_client",
                method=method,
                operation="READ",
                params=safe_params,
                result="failure",
                error=code,
            )
            raise BitrixError(f"Bitrix returned {code} for {method}")
        self.audit.record(
            tool="bitrix_client",
            method=method,
            operation="READ",
            params=safe_params,
            result="success",
        )
        return payload.get("result")
