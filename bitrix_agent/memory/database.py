from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, user_goal TEXT NOT NULL,
  mechanism TEXT NOT NULL, rest_methods TEXT NOT NULL, required_fields TEXT NOT NULL,
  steps TEXT NOT NULL, constraints TEXT NOT NULL, verification_result TEXT,
  status TEXT NOT NULL CHECK(status IN ('draft','tested','verified','deprecated')),
  last_success_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS experiments (
  id INTEGER PRIMARY KEY, goal TEXT NOT NULL, method TEXT NOT NULL, params TEXT NOT NULL,
  result TEXT, error TEXT, success INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bitrix_map (
  id INTEGER PRIMARY KEY, kind TEXT NOT NULL, external_id TEXT NOT NULL DEFAULT '',
  name TEXT NOT NULL DEFAULT '', data TEXT NOT NULL, observed_at TEXT NOT NULL,
  UNIQUE(kind, external_id, name)
);
"""


class Memory:
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            connection.executescript(SCHEMA)
            yield connection
            connection.commit()
        finally:
            connection.close()

    def experiment(
        self,
        goal: str,
        method: str,
        params: dict[str, Any],
        *,
        result: Any = None,
        error: str | None = None,
        success: bool,
    ) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO experiments(goal,method,params,result,error,success,created_at) VALUES(?,?,?,?,?,?,?)",
                (goal, method, _json(params), _json(result), error, int(success), _now()),
            )

    def map_item(self, kind: str, external_id: str, name: str, data: Any) -> None:
        with self.connect() as db:
            db.execute(
                """INSERT INTO bitrix_map(kind,external_id,name,data,observed_at) VALUES(?,?,?,?,?)
                ON CONFLICT(kind,external_id,name) DO UPDATE SET data=excluded.data,
                observed_at=excluded.observed_at""",
                (kind, external_id, name, _json(data), _now()),
            )


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _now() -> str:
    return datetime.now(UTC).isoformat()
