from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import ConfigError, ThreadsSettings
from .post_runner import build_post_plans, load_posts, run_posts, save_run_output
from .threads_client import ThreadsApiError, ThreadsClient


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "publish":
            return _publish(args)
        if args.command == "validate-env":
            return _validate_env()
        if args.command == "resolve-user-id":
            return _resolve_user_id(args)
        if args.command == "refresh-token":
            return _refresh_token(args)
        if args.command == "exchange-token":
            return _exchange_token(args)
    except (ConfigError, ThreadsApiError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="threads-auto-poster")
    subparsers = parser.add_subparsers(dest="command", required=True)
    publish = subparsers.add_parser("publish")
    source = publish.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--file", type=Path)
    publish.add_argument("--output", type=Path, default=Path("dist/publish-result.json"))
    publish.add_argument("--dry-run", action="store_true")
    publish.add_argument("--execute", action="store_true")
    publish.add_argument("--user-id")
    publish.add_argument("--reply-control", choices=["everyone", "accounts_you_follow", "mentioned_only"])
    publish.add_argument("--topic-tag")
    publish.add_argument("--link-attachment")
    subparsers.add_parser("validate-env")
    resolve = subparsers.add_parser("resolve-user-id")
    resolve.add_argument("--execute", action="store_true")
    refresh = subparsers.add_parser("refresh-token")
    refresh.add_argument("--execute", action="store_true")
    refresh.add_argument("--token")
    exchange = subparsers.add_parser("exchange-token")
    exchange.add_argument("--execute", action="store_true")
    exchange.add_argument("--short-lived-token", required=True)
    return parser


def _publish(args: argparse.Namespace) -> int:
    if args.execute and args.dry_run:
        raise ValueError("Use either --dry-run or --execute, not both")
    dry_run = not args.execute
    settings = ThreadsSettings.from_env(require_access_token=args.execute)
    if settings.dry_run and not args.execute:
        dry_run = True
    texts = [args.text] if args.text is not None else load_posts(args.file)
    plans = build_post_plans(texts)
    client = None
    user_id = args.user_id or settings.user_id or "me"
    if not dry_run:
        assert settings.access_token is not None
        client = ThreadsClient(
            access_token=settings.access_token,
            base_url=settings.base_url,
            graph_root_url=settings.graph_root_url,
            timeout_seconds=settings.timeout_seconds,
        )
    results = run_posts(
        plans,
        dry_run=dry_run,
        client=client,
        user_id=user_id,
        reply_control=args.reply_control,
        topic_tag=args.topic_tag,
        link_attachment=args.link_attachment,
    )
    save_run_output(args.output, dry_run=dry_run, results=results)
    print(json.dumps({"dry_run": dry_run, "output": str(args.output), "count": len(results)}, indent=2))
    return 0 if all(result.status != "error" for result in results) else 1


def _validate_env() -> int:
    settings = ThreadsSettings.from_env(require_access_token=False)
    print(json.dumps(settings.public_status(), indent=2, ensure_ascii=False))
    return 0


def _resolve_user_id(args: argparse.Namespace) -> int:
    if not args.execute:
        print("dry-run: add --execute to call Threads /me")
        return 0
    settings = ThreadsSettings.from_env(require_access_token=True)
    assert settings.access_token is not None
    client = ThreadsClient(access_token=settings.access_token, base_url=settings.base_url, graph_root_url=settings.graph_root_url)
    data = client.get_me()
    print(json.dumps({"id": data.get("id"), "username": data.get("username")}, indent=2))
    return 0


def _refresh_token(args: argparse.Namespace) -> int:
    if not args.execute:
        print("dry-run: add --execute to call Threads refresh_access_token")
        return 0
    settings = ThreadsSettings.from_env(require_access_token=not args.token)
    token = args.token or settings.access_token
    if not token:
        raise ConfigError("A token is required")
    client = ThreadsClient(access_token=token, base_url=settings.base_url, graph_root_url=settings.graph_root_url)
    print(_redact_token_payload(client.refresh_long_lived_token(long_lived_token=token)))
    return 0


def _exchange_token(args: argparse.Namespace) -> int:
    if not args.execute:
        print("dry-run: add --execute to call Threads access_token exchange")
        return 0
    settings = ThreadsSettings.from_env(require_access_token=False)
    if not settings.app_secret:
        raise ConfigError("THREADS_APP_SECRET is required to exchange tokens")
    client = ThreadsClient(access_token=args.short_lived_token, base_url=settings.base_url, graph_root_url=settings.graph_root_url)
    print(_redact_token_payload(client.exchange_long_lived_token(short_lived_token=args.short_lived_token, app_secret=settings.app_secret)))
    return 0


def _redact_token_payload(data: dict[str, object]) -> str:
    safe = dict(data)
    if "access_token" in safe:
        safe["access_token"] = "<redacted>"
    return json.dumps(safe, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    raise SystemExit(main())
