#!/usr/bin/env python3
"""AgentArts low-code single-agent HTTP/SSE API probe.

Protocol sources and setup: docs/低码API接入_2026-11-02.md.
Only Bearer API Key authentication is implemented. No automatic retries or writes.
"""
import argparse
import json
import math
import os
import re
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class ProbeError(Exception):
    """Only controlled, non-sensitive messages may be exposed by the CLI."""


def validate_url(value):
    try:
        url = urlsplit(value)
        valid = (url.scheme == 'https' and url.hostname and not url.username
                 and not url.password and not url.query and not url.fragment
                 and url.port in (None, 443)
                 and re.fullmatch(r'/runtimes/[A-Za-z0-9_-]{1,64}/invocations', url.path)
                 and not any(ord(c) <= 32 or ord(c) == 127 for c in value))
    except ValueError:
        valid = False
    if not valid:
        raise ProbeError('请使用控制台提供的HTTPS调用路径：/runtimes/{运行时名称}/invocations。')
    return value


def sse_events(lines):
    """Decode SSE framing, including comments, CRLF and multiline data fields."""
    data = []
    size = 0
    for raw in lines:
        if len(raw) > 1024 * 1024:
            raise ProbeError('响应事件过大，已停止。')
        try:
            line = raw.decode('utf-8').rstrip('\r\n')
        except UnicodeDecodeError:
            raise ProbeError('响应不是有效UTF-8文本。') from None
        if not line:
            if data:
                yield decode_event('\n'.join(data))
            data, size = [], 0
        elif line.startswith('data:'):
            part = line[5:].removeprefix(' ')
            size += len(part)
            if size > 1024 * 1024:
                raise ProbeError('响应事件过大，已停止。')
            data.append(part)
    if data:
        yield decode_event('\n'.join(data))


def decode_event(value):
    try:
        event = json.loads(value)
    except (ValueError, RecursionError):
        raise ProbeError('响应事件不是有效JSON，调用未通过。') from None
    if not isinstance(event, dict):
        raise ProbeError('响应事件格式不符，调用未通过。')
    return event


def collect_reply(events):
    """Read single-agent final content only; discard reasoning and tool payloads."""
    chunks, summary, latency = [], None, {}
    total_chars = 0
    for event in events:
        kind = event.get('event')
        if kind in ('error', 'exception'):
            raise ProbeError('平台报告执行失败，请到控制台查看详情。')
        if kind == 'message' and isinstance(event.get('content'), str):
            chunks.append(event['content'])
            total_chars += len(event['content'])
        elif kind == 'summary_response' and isinstance(event.get('content'), str):
            summary = event['content']
            total_chars += len(summary)
        elif kind == 'statistic_data' and isinstance(event.get('latency'), dict):
            latency = {k: v for k, v in event['latency'].items()
                       if k in ('overall', 'model', 'plugin') and type(v) in (int, float)
                       and math.isfinite(v) and v >= 0}
        elif kind in ('end', 'done'):
            # Official docs use end; deployed single-agent API observed done (2026-11-02).
            reply = summary if summary is not None else ''.join(chunks)
            if not reply.strip():
                raise ProbeError('响应已结束但没有最终回答，调用未通过。')
            return reply, latency
        if total_chars > 2 * 1024 * 1024:
            raise ProbeError('回答过大，已停止。')
    raise ProbeError('连接在结束事件之前中断，调用未通过。')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward an Authorization header to another destination.
        raise ProbeError('接口返回重定向，未转发凭据；请核对调用路径。')


def invoke(url, key, session_id, message, timeout=180):
    validate_url(url)
    if not key or any(ord(c) <= 32 or ord(c) == 127 for c in key):
        raise ProbeError('请配置低码应用的API Key，只填密钥本身。')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', session_id):
        raise ProbeError('会话ID只允许英文、数字、-、_，长度1—64。')
    if not message.strip() or not 0 < timeout <= 600:
        raise ProbeError('消息不能为空；单次网络读取超时应在0—600秒之间。')
    body = json.dumps({'query': message, 'inputs': {}}, ensure_ascii=False).encode()
    request = Request(url, data=body, method='POST', headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'X-Invoke-Mode': 'published',
        'x-hw-agentarts-session-id': session_id,
        'X-Request-Id': uuid.uuid4().hex,
    })
    try:
        with build_opener(NoRedirect).open(request, timeout=timeout) as response:
            if response.status != 200:
                raise ProbeError('接口未返回成功状态，调用未通过。')
            if response.headers.get_content_type() != 'text/event-stream':
                raise ProbeError('接口未返回SSE流，请核对应用和协议。')
            return collect_reply(sse_events(iter(lambda: response.readline(1024 * 1024 + 1), b'')))
    except HTTPError as exc:
        raise ProbeError(f'接口返回HTTP {exc.code}，请核对部署、鉴权和配额。') from None
    except (URLError, TimeoutError, OSError):
        raise ProbeError('网络调用失败或读取超时；重试前请先查看平台执行状态。') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default=os.getenv('AGENTARTS_LOWCODE_URL', ''))
    parser.add_argument('--session-id', default=uuid.uuid4().hex)
    parser.add_argument('--message', default='你好，请用一句话介绍你能帮助我做什么。')
    parser.add_argument('--timeout', type=float, default=180, help='单次网络读取超时秒数')
    parser.add_argument('--dry-run', action='store_true', help='仅离线检查参数，不读取密钥')
    args = parser.parse_args()
    try:
        validate_url(args.url)
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', args.session_id):
            raise ProbeError('会话ID格式不符。')
        if not args.message.strip() or not 0 < args.timeout <= 600:
            raise ProbeError('消息或超时参数不合法。')
        if args.dry_run:
            print('低码API参数检查通过；未读取密钥、未调用云端。')
            return 0
        key = os.getenv('AGENTARTS_LOWCODE_API_KEY', '').strip()
        start = time.monotonic()
        reply, latency = invoke(args.url, key, args.session_id, args.message, args.timeout)
        print(f'会话ID：{args.session_id}\n回复：\n{reply.replace(key, "[已隐藏]")}')
        print(f'调用完成，用时{time.monotonic() - start:.1f}秒；业务保存与回答质量未验收。')
        if latency:
            print('平台耗时（秒）：' + json.dumps(latency))
        return 0
    except ProbeError as exc:
        print(str(exc), file=sys.stderr)
    except Exception:
        # Never print raw response bodies, headers, URLs or third-party errors.
        print('调用异常，未判定通过；请在平台核查。', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
