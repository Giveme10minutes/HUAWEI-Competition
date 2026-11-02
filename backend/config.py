"""Local-only configuration for the prototype web app.

Only the backend reads this module. The browser never receives the low-code
URL, API key, or any other credential.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT / "local_data" / "app.sqlite3"
DEFAULT_TIMEOUT = 180.0


def _parse_dotenv(path: Path) -> dict[str, str]:
    """Parse simple KEY=VALUE lines without executing anything.

    The real environment always wins. Values are stripped and surrounding
    quotes are removed; comments and malformed lines are ignored.
    """
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def _read(name: str, dotenv: dict[str, str]) -> str:
    if name in os.environ:
        return os.environ[name].strip()
    return dotenv.get(name, "").strip()


def _read_timeout(dotenv: dict[str, str]) -> float:
    raw = _read("AGENTARTS_LOWCODE_TIMEOUT", dotenv)
    if not raw:
        return DEFAULT_TIMEOUT
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_TIMEOUT
    return min(600.0, max(10.0, value))


def _read_db_path(dotenv: dict[str, str]) -> Path:
    raw = _read("APP_DB_PATH", dotenv)
    if not raw:
        return DEFAULT_DB_PATH
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    lowcode_url: str
    lowcode_api_key: str
    agent_timeout: float = DEFAULT_TIMEOUT
    timezone: str = "Asia/Shanghai"


def load_settings() -> Settings:
    dotenv = _parse_dotenv(ROOT / ".env")
    return Settings(
        db_path=_read_db_path(dotenv),
        lowcode_url=_read("AGENTARTS_LOWCODE_URL", dotenv),
        lowcode_api_key=_read("AGENTARTS_LOWCODE_API_KEY", dotenv),
        agent_timeout=_read_timeout(dotenv),
    )
