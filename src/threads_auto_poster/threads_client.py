from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class ThreadsApiError(RuntimeError):
    """Raised when Threads API returns an error response."""


@dataclass(frozen=True)
class PublishResult:
    container_id: str
    post_id: str
    raw_publish_response: dict[str, Any]


class ThreadsClient:
    """Small Threads API client. Network calls happen only when methods are called."""

    def __init__(
        self,
        *,
        access_token: str,
        base_url: str = "https://graph.threads.net/v1.0",
        graph_root_url: str = "https://graph.threads.net",
        timeout_seconds: int = 30,
        session: requests.Session | None = None,
    ) -> None:
        if not access_token:
            raise ValueError("access_token is required")
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")
        self.graph_root_url = graph_root_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def get_me(self) -> dict[str, Any]:
        return self._request("GET", f"{self.base_url}/me", params={"fields": "id,username"})

    def get_me_id(self) -> str:
        data = self.get_me()
        user_id = data.get("id")
        if not user_id:
            raise ThreadsApiError("Threads /me response did not include id")
        return str(user_id)

    def create_text_container(
        self,
        *,
        text: str,
        user_id: str = "me",
        reply_control: str | None = None,
        topic_tag: str | None = None,
        link_attachment: str | None = None,
    ) -> str:
        payload: dict[str, str] = {"media_type": "TEXT", "text": text}
        if reply_control:
            payload["reply_control"] = reply_control
        if topic_tag:
            payload["topic_tag"] = topic_tag
        if link_attachment:
            payload["link_attachment"] = link_attachment
        data = self._request("POST", f"{self.base_url}/{user_id}/threads", data=payload)
        container_id = data.get("id")
        if not container_id:
            raise ThreadsApiError("Threads container response did not include id")
        return str(container_id)

    def publish_container(self, *, creation_id: str, user_id: str = "me") -> dict[str, Any]:
        return self._request(
            "POST",
            f"{self.base_url}/{user_id}/threads_publish",
            data={"creation_id": creation_id},
        )

    def publish_text_post(
        self,
        *,
        text: str,
        user_id: str = "me",
        reply_control: str | None = None,
        topic_tag: str | None = None,
        link_attachment: str | None = None,
    ) -> PublishResult:
        container_id = self.create_text_container(
            text=text,
            user_id=user_id,
            reply_control=reply_control,
            topic_tag=topic_tag,
            link_attachment=link_attachment,
        )
        publish_response = self.publish_container(creation_id=container_id, user_id=user_id)
        post_id = str(publish_response.get("id", ""))
        if not post_id:
            raise ThreadsApiError("Threads publish response did not include id")
        return PublishResult(container_id, post_id, publish_response)

    def exchange_long_lived_token(self, *, short_lived_token: str, app_secret: str) -> dict[str, Any]:
        return self._request_without_bearer(
            "GET",
            f"{self.graph_root_url}/access_token",
            params={
                "grant_type": "th_exchange_token",
                "client_secret": app_secret,
                "access_token": short_lived_token,
            },
        )

    def refresh_long_lived_token(self, *, long_lived_token: str) -> dict[str, Any]:
        return self._request_without_bearer(
            "GET",
            f"{self.graph_root_url}/refresh_access_token",
            params={"grant_type": "th_refresh_token", "access_token": long_lived_token},
        )

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        return self._send(method, url, headers=headers, params=params, data=data)

    def _request_without_bearer(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._send(method, url, headers={}, params=params, data=data)

    def _send(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, Any] | None,
        data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        response = self.session.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            timeout=self.timeout_seconds,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw_text": response.text}
        if response.status_code >= 400:
            raise ThreadsApiError(f"Threads API error {response.status_code}: {_extract_error_message(payload)}")
        if not isinstance(payload, dict):
            raise ThreadsApiError("Threads API returned a non-object JSON response")
        return payload


def _extract_error_message(payload: Any) -> str:
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            return str(error.get("message") or error)
        return str(payload.get("message") or payload)
    return str(payload)
