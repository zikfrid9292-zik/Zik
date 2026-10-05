from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(RuntimeError):
    """A safe, secret-free configuration error."""


def load_dotenv(path: Path = Path(".env")) -> None:
    """Load a minimal KEY=VALUE dotenv without overriding the process environment."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    webhook_url: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        value = os.getenv("BITRIX_WEBHOOK_URL", "").strip()
        if not value:
            raise ConfigurationError(
                "BITRIX_WEBHOOK_URL is missing; add it to a local .env to run READ-only discovery"
            )
        if not value.startswith("https://"):
            raise ConfigurationError("BITRIX_WEBHOOK_URL must use HTTPS")
        return cls(webhook_url=value.rstrip("/"))
