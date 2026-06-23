from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .threads_client import ThreadsClient

MAX_THREADS_TEXT_CHARS = 500


class PostValidationError(ValueError):
    """Raised when post content cannot be published safely."""


@dataclass(frozen=True)
class PostPlan:
    index: int
    text: str
    char_count: int


@dataclass(frozen=True)
class PostRunResult:
    index: int
    status: str
    text_preview: str
    char_count: int
    container_id: str | None = None
    post_id: str | None = None
    error: str | None = None


def load_posts(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json_posts(path)
    if suffix == ".csv":
        return _load_csv_posts(path)
    return _load_text_posts(path)


def build_post_plans(texts: list[str], *, max_chars: int = MAX_THREADS_TEXT_CHARS) -> list[PostPlan]:
    plans: list[PostPlan] = []
    for index, text in enumerate(texts, start=1):
        normalized = text.strip()
        if not normalized:
            continue
        validate_post_text(normalized, max_chars=max_chars)
        plans.append(PostPlan(index=index, text=normalized, char_count=len(normalized)))
    if not plans:
        raise PostValidationError("No publishable posts were found")
    return plans


def validate_post_text(text: str, *, max_chars: int = MAX_THREADS_TEXT_CHARS) -> None:
    if not text.strip():
        raise PostValidationError("Post text is empty")
    if len(text) > max_chars:
        raise PostValidationError(
            f"Post text is {len(text)} characters, exceeding the {max_chars} character limit"
        )


def run_posts(
    plans: list[PostPlan],
    *,
    dry_run: bool,
    client: ThreadsClient | None = None,
    user_id: str = "me",
    reply_control: str | None = None,
    topic_tag: str | None = None,
    link_attachment: str | None = None,
) -> list[PostRunResult]:
    if not dry_run and client is None:
        raise ValueError("client is required when dry_run is false")
    results: list[PostRunResult] = []
    for plan in plans:
        if dry_run:
            results.append(PostRunResult(plan.index, "dry_run", _preview(plan.text), plan.char_count))
            continue
        assert client is not None
        try:
            published = client.publish_text_post(
                text=plan.text,
                user_id=user_id,
                reply_control=reply_control,
                topic_tag=topic_tag,
                link_attachment=link_attachment,
            )
        except Exception as exc:  # noqa: BLE001
            results.append(PostRunResult(plan.index, "error", _preview(plan.text), plan.char_count, error=str(exc)))
            continue
        results.append(
            PostRunResult(
                plan.index,
                "published",
                _preview(plan.text),
                plan.char_count,
                container_id=published.container_id,
                post_id=published.post_id,
            )
        )
    return results


def save_run_output(path: Path, *, dry_run: bool, results: list[PostRunResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "dry_run": dry_run,
        "summary": {
            "total": len(results),
            "published": sum(1 for item in results if item.status == "published"),
            "errors": sum(1 for item in results if item.status == "error"),
        },
        "results": [asdict(result) for result in results],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_json_posts(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(item) for item in data]
    if isinstance(data, dict) and isinstance(data.get("posts"), list):
        return [str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in data["posts"]]
    raise PostValidationError("JSON input must be a list of strings or {'posts': [...]}")


def _load_csv_posts(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames and "text" in reader.fieldnames:
            return [row.get("text", "") for row in reader]
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        return [row[0] for row in reader if row]


def _load_text_posts(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _preview(text: str, *, length: int = 80) -> str:
    return text if len(text) <= length else f"{text[: length - 1]}…"
