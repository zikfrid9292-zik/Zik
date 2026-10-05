from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bitrix_agent.core.audit import AuditLogger
from bitrix_agent.core.bitrix_client import BitrixClient
from bitrix_agent.core.config import ConfigurationError, Settings
from bitrix_agent.memory.database import Memory
from bitrix_agent.planner.discovery import TestProjectDiscovery


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["discover-test"])
    parser.add_argument("--db", type=Path, default=Path("var/agent-v3.sqlite3"))
    args = parser.parse_args()
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    memory = Memory(args.db)
    client = BitrixClient(settings.webhook_url, AuditLogger(Path("var/audit.jsonl")))
    report = TestProjectDiscovery(client, memory).run()
    summary = {
        "memory": str(args.db),
        "method_checks": len(report["methods"]),
        "available_methods": sorted(
            name
            for name, state in report["methods"].items()
            if isinstance(state, dict) and state.get("isAvailable")
        ),
        "sections": {name: _status(value) for name, value in report.items() if name != "methods"},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _status(value: object) -> str:
    if isinstance(value, dict) and value.get("status") in {"error", "unavailable"}:
        return str(value["status"])
    return "stored"


if __name__ == "__main__":
    raise SystemExit(main())
