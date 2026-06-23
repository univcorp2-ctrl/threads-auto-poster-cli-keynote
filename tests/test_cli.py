from __future__ import annotations

import json

from threads_auto_poster.cli import main


def test_publish_dry_run_text(tmp_path):
    output = tmp_path / "result.json"
    code = main(["publish", "--text", "hello threads", "--dry-run", "--output", str(output)])
    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["dry_run"] is True
    assert payload["summary"]["total"] == 1
    assert payload["results"][0]["status"] == "dry_run"


def test_resolve_user_id_without_execute_does_not_call_api(capsys):
    code = main(["resolve-user-id"])
    captured = capsys.readouterr()
    assert code == 0
    assert "dry-run" in captured.out
