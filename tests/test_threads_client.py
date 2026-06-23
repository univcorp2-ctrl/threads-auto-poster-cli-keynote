from __future__ import annotations

from threads_auto_poster.threads_client import ThreadsClient


class FakeResponse:
    status_code = 200
    text = ""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, headers=None, params=None, data=None, timeout=None):
        self.calls.append({"method": method, "url": url, "headers": headers, "params": params, "data": data, "timeout": timeout})
        if url.endswith("/threads"):
            return FakeResponse({"id": "container-123"})
        if url.endswith("/threads_publish"):
            return FakeResponse({"id": "post-456"})
        return FakeResponse({"id": "user-1", "username": "demo"})


def test_publish_text_post_uses_two_step_flow():
    session = FakeSession()
    client = ThreadsClient(access_token="token", session=session)
    result = client.publish_text_post(text="hello", user_id="me")
    assert result.container_id == "container-123"
    assert result.post_id == "post-456"
    assert len(session.calls) == 2
    assert session.calls[0]["url"].endswith("/me/threads")
    assert session.calls[1]["url"].endswith("/me/threads_publish")
