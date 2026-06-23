from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing."""


TRUE_VALUES = {"1", "true", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "no", "n", "off"}


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    normalized = raw.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be a boolean value, got: {raw!r}")


@dataclass(frozen=True)
class ThreadsSettings:
    app_id: str | None
    app_secret: str | None
    access_token: str | None
    user_id: str | None
    dry_run: bool
    base_url: str = "https://graph.threads.net/v1.0"
    graph_root_url: str = "https://graph.threads.net"
    timeout_seconds: int = 30

    @classmethod
    def from_env(cls, *, require_access_token: bool = False) -> "ThreadsSettings":
        load_dotenv()
        timeout_raw = os.getenv("THREADS_TIMEOUT_SECONDS", "30")
        try:
            timeout_seconds = int(timeout_raw)
        except ValueError as exc:
            raise ConfigError("THREADS_TIMEOUT_SECONDS must be an integer") from exc

        settings = cls(
            app_id=_blank_to_none(os.getenv("THREADS_APP_ID")),
            app_secret=_blank_to_none(os.getenv("THREADS_APP_SECRET")),
            access_token=_blank_to_none(os.getenv("THREADS_ACCESS_TOKEN")),
            user_id=_blank_to_none(os.getenv("THREADS_USER_ID")),
            dry_run=env_bool("THREADS_DRY_RUN", True),
            base_url=os.getenv("THREADS_API_BASE_URL", "https://graph.threads.net/v1.0").rstrip("/"),
            graph_root_url=os.getenv("THREADS_GRAPH_ROOT_URL", "https://graph.threads.net").rstrip("/"),
            timeout_seconds=timeout_seconds,
        )
        if require_access_token and not settings.access_token:
            raise ConfigError("THREADS_ACCESS_TOKEN is required for --execute")
        return settings

    def public_status(self) -> dict[str, bool | str | int]:
        return {
            "has_app_id": bool(self.app_id),
            "has_app_secret": bool(self.app_secret),
            "has_access_token": bool(self.access_token),
            "has_user_id": bool(self.user_id),
            "dry_run": self.dry_run,
            "base_url": self.base_url,
            "timeout_seconds": self.timeout_seconds,
        }


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None
