"""Agent transport adapter.

This module is the only place that knows the AgentArts low-code HTTP/SSE
protocol. The web layer and SQLite storage stay independent so a Managed
Agents transport can be added later without mixing the two protocols.
"""

from __future__ import annotations

import json
import math
import re
import uuid
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

SESSION_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
URL_PATH_RE = re.compile(r"/runtimes/[A-Za-z0-9_-]{1,64}/invocations")
MAX_EVENT_BYTES = 1024 * 1024
MAX_REPLY_CHARS = 2 * 1024 * 1024


class AgentError(Exception):
    """A controlled failure whose message is safe to show in the UI."""

    def __init__(self, message: str, code: str = "agent_error"):
        super().__init__(message)
        self.message = message
        self.code = code


class _ProtocolError(Exception):
    pass


@dataclass(frozen=True)
class AgentReply:
    text: str
    latency: dict[str, float] = field(default_factory=dict)


class AgentClient(Protocol):
    @property
    def configured(self) -> bool: ...

    def reply(self, session_id: str, message: str) -> AgentReply: ...


def _validate_url(value: str) -> str:
    try:
        url = urlsplit(value)
        valid = (
            url.scheme == "https"
            and bool(url.hostname)
            and not url.username
            and not url.password
            and not url.query
            and not url.fragment
            and url.port in (None, 443)
            and URL_PATH_RE.fullmatch(url.path) is not None
            and not any(ord(char) <= 32 or ord(char) == 127 for char in value)
        )
    except ValueError:
        valid = False
    if not valid:
        raise _ProtocolError("低码调用地址格式不符。")
    return value


def _sse_events(lines: Iterable[bytes]) -> Iterator[dict]:
    data: list[str] = []
    size = 0
    for raw in lines:
        if len(raw) > MAX_EVENT_BYTES:
            raise _ProtocolError("响应事件过大。")
        try:
            line = raw.decode("utf-8").rstrip("\r\n")
        except UnicodeDecodeError:
            raise _ProtocolError("响应不是有效 UTF-8 文本。") from None
        if not line:
            if data:
                yield _decode_event("\n".join(data))
            data, size = [], 0
        elif line.startswith("data:"):
            part = line[5:].removeprefix(" ")
            size += len(part)
            if size > MAX_EVENT_BYTES:
                raise _ProtocolError("响应事件过大。")
            data.append(part)
    if data:
        yield _decode_event("\n".join(data))


def _decode_event(value: str) -> dict:
    try:
        event = json.loads(value)
    except (ValueError, RecursionError):
        raise _ProtocolError("响应事件不是有效 JSON。") from None
    if not isinstance(event, dict):
        raise _ProtocolError("响应事件格式不符。")
    return event


def _collect_reply(events: Iterable[dict]) -> tuple[str, dict[str, float]]:
    """Keep only the final answer; reasoning and tool payloads are ignored."""
    chunks: list[str] = []
    summary: str | None = None
    latency: dict[str, float] = {}
    total_chars = 0
    for event in events:
        kind = event.get("event")
        if kind in ("error", "exception"):
            raise _ProtocolError("平台报告执行失败。")
        if kind == "message" and isinstance(event.get("content"), str):
            chunks.append(event["content"])
            total_chars += len(event["content"])
        elif kind == "summary_response" and isinstance(event.get("content"), str):
            summary = event["content"]
            total_chars += len(summary)
        elif kind == "statistic_data" and isinstance(event.get("latency"), dict):
            latency = {
                key: value
                for key, value in event["latency"].items()
                if key in ("overall", "model", "plugin")
                and type(value) in (int, float)
                and math.isfinite(value)
                and value >= 0
            }
        elif kind in ("end", "done"):
            reply = summary if summary is not None else "".join(chunks)
            if not reply.strip():
                raise _ProtocolError("响应已结束但没有最终回答。")
            return reply, latency
        if total_chars > MAX_REPLY_CHARS:
            raise _ProtocolError("回答过大。")
    raise _ProtocolError("连接在结束事件之前中断。")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise _ProtocolError("接口返回重定向，未转发凭据。")


class LowCodeAgent:
    """AgentArts low-code single-agent transport (HTTP + SSE)."""

    def __init__(self, url: str, api_key: str, timeout: float = 180.0):
        self._url = (url or "").strip()
        self._key = (api_key or "").strip()
        self._timeout = timeout
        self._configured = False
        try:
            _validate_url(self._url)
            if not self._key or any(
                ord(char) <= 32 or ord(char) == 127 for char in self._key
            ):
                raise _ProtocolError("低码 API Key 缺失。")
        except _ProtocolError:
            return
        self._configured = True

    @property
    def configured(self) -> bool:
        return self._configured

    def reply(self, session_id: str, message: str) -> AgentReply:
        if not self._configured:
            raise AgentError(
                "在线助手尚未连接；你的消息已保存在本地，可稍后重试。",
                "not_configured",
            )
        if not SESSION_RE.fullmatch(session_id):
            raise AgentError("会话标识无效，无法调用助手。", "bad_session")
        if not message.strip():
            raise AgentError("消息不能为空。", "empty_message")

        body = json.dumps(
            {"query": message, "inputs": {}}, ensure_ascii=False
        ).encode("utf-8")
        request = Request(
            self._url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "X-Invoke-Mode": "published",
                "x-hw-agentarts-session-id": session_id,
                "X-Request-Id": uuid.uuid4().hex,
            },
        )
        try:
            with build_opener(_NoRedirect).open(
                request, timeout=self._timeout
            ) as response:
                if response.status != 200:
                    raise _ProtocolError("接口未返回成功状态。")
                if response.headers.get_content_type() != "text/event-stream":
                    raise _ProtocolError("接口未返回事件流。")
                text, latency = _collect_reply(
                    _sse_events(
                        iter(lambda: response.readline(MAX_EVENT_BYTES + 1), b"")
                    )
                )
        except HTTPError as exc:
            if exc.code in (401, 403):
                raise AgentError(
                    "助手鉴权未通过，请检查本地调用配置后重试。", "unauthorized"
                ) from None
            if exc.code == 429:
                raise AgentError(
                    "助手调用次数受限，请稍后重试；你的消息已保存。", "rate_limited"
                ) from None
            if exc.code == 404:
                raise AgentError(
                    "助手调用地址不可用，请检查本地调用配置后重试。", "not_found"
                ) from None
            raise AgentError(
                "助手服务暂时不可用，请稍后重试；你的消息已保存。",
                "upstream_unavailable",
            ) from None
        except AgentError:
            raise
        except _ProtocolError as exc:
            raise AgentError(
                f"助手返回内容异常（{exc}），请重试。", "protocol_error"
            ) from None
        except (URLError, TimeoutError, OSError):
            raise AgentError(
                "连接助手失败或超时，请稍后重试；你的消息已保存。", "network_error"
            ) from None
        except Exception:
            raise AgentError("调用助手时出现异常，请稍后重试。", "unexpected") from None

        text = text.strip()
        if self._key:
            text = text.replace(self._key, "[已隐藏]")
        if not text:
            raise AgentError("助手没有返回可用回答，请重试。", "empty_reply")
        return AgentReply(text=text, latency=latency)
