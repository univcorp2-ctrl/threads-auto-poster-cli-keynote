from __future__ import annotations

import json

import pytest

from threads_auto_poster.post_runner import PostValidationError, build_post_plans, load_posts, run_posts


def test_build_post_plans_rejects_long_text():
    with pytest.raises(PostValidationError):
        build_post_plans(["x" * 501])


def test_load_json_posts(tmp_path):
    path = tmp_path / "posts.json"
    path.write_text(json.dumps({"posts": [{"text": "one"}, {"text": "two"}]}), encoding="utf-8")
    assert load_posts(path) == ["one", "two"]


def test_run_posts_dry_run_requires_no_client():
    plans = build_post_plans(["hello"])
    results = run_posts(plans, dry_run=True)
    assert results[0].status == "dry_run"
    assert results[0].post_id is None
