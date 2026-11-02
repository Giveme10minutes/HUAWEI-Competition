#!/usr/bin/env python3
"""Managed Agents 连通测试；协议参照 references/official/agentarts 中官方客户端。

仅测试 API Key 入站认证。不会自动授权工具或代答选择题。
"""
import argparse
import asyncio
import json
import os
import re
import sys
import time
import uuid
from urllib.parse import urlsplit


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default=os.getenv('AGENTARTS_WS_URL', ''))
    parser.add_argument('--session-id', default=uuid.uuid4().hex)
    parser.add_argument('--message', default='你好，请用一句话介绍你能帮助我做什么。')
    parser.add_argument('--timeout', type=float, default=120, help='整个调用的超时秒数')
    parser.add_argument('--dry-run', action='store_true', help='离线检查参数，不读取密钥、不调用云端')
    args = parser.parse_args()
    url = urlsplit(args.url)
    if url.scheme not in ('ws', 'wss') or not url.hostname or url.username or url.password or url.query or url.fragment:
        parser.error('请设置有效的 AGENTARTS_WS_URL（ws:// 或 wss://，不包含密钥、查询参数）')
    if not re.fullmatch(r'/runtimes/[^/]+/ws', url.path):
        parser.error('地址路径应为 /runtimes/{运行时名称}/ws')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', args.session_id):
        parser.error('会话 ID 只能含英文、数字、-、_，长度 1—64')
    if not 0 < args.timeout <= 3600:
        parser.error('超时必须在 0—3600 秒之间')
    if not args.message.strip():
        parser.error('消息不能为空')
    return args


async def exchange(args, key):
    try:
        from websockets.asyncio.client import connect
    except ImportError:
        raise RuntimeError('请先安装依赖：python -m pip install -r scripts/requirements-agentarts.txt') from None
    url = urlsplit(args.url)
    headers = {
        'Authorization': f'Bearer {key}',
        'x-hw-agentarts-session-id': args.session_id,
        'X-HW-AgentArts-Claw-User-Id': 'user_default',
        'X-HW-AgentGateway-Chat-Id': 'chat1',
        'Origin': f'{"https" if url.scheme == "wss" else "http"}://{url.netloc}',
    }
    async with connect(args.url, additional_headers=headers, compression=None,
                       open_timeout=min(args.timeout, 30)) as ws:
        print('已连接，等待服务端就绪……', flush=True)
        while True:
            frame = json.loads(await ws.recv())
            if frame.get('type') == 'event' and frame.get('event') == 'connection.ack':
                break
            if frame.get('response_kind') == 'e2a.error' or frame.get('status') == 'failed':
                raise RuntimeError('服务端在就绪前返回失败')
        # 保持官方协议：握手会话 ID 与消息体 session_default 不是同一个字段。
        await ws.send(json.dumps({
            'request_id': str(uuid.uuid4()), 'channel_id': 'officeclaw',
            'session_id': 'session_default', 'chat_id': 'chat1',
            'req_method': 'chat.send',
            'params': {'query': args.message, 'mode': 'agent.plan', 'interactive_ask': True},
            'metadata': {'user_id': 'user_default'}, 'is_stream': True,
            'timestamp': time.time(),
        }, ensure_ascii=False))
        chunks = []
        while True:
            frame = json.loads(await ws.recv())
            body = frame.get('body') or {}
            payload = frame.get('payload') or {}
            result = body.get('result') or {}
            event = (result.get('event_type') if frame.get('is_final') else body.get('event_type')) or payload.get('event_type', '')
            if frame.get('tag') == 'TOOL_PERMISSION' and frame.get('decision') == 'ASK':
                raise RuntimeError('收到工具授权请求，已停止；请到平台检查并人工确认')
            if event == 'chat.ask_user_question':
                raise RuntimeError('收到交互选择题，已停止；本脚本不自动代答，请到平台调试')
            if frame.get('response_kind') == 'e2a.error' or frame.get('status') in ('failed', 'cancelled') or event == 'chat.error':
                raise RuntimeError('服务端返回失败；请在平台检查运行记录')
            if frame.get('is_final') or event == 'chat.final':
                content = result.get('content') if frame.get('response_kind') else payload.get('content')
                reply = content if isinstance(content, str) and content.strip() else ''.join(chunks)
                if not reply.strip():
                    raise RuntimeError('已结束但没有文本回复，不能判定连通测试通过')
                return reply
            delta = body.get('delta') if frame.get('response_kind') else payload.get('content')
            if isinstance(delta, str) and event in ('chat.delta', ''):
                chunks.append(delta)
            if event == 'chat.done' or frame.get('is_complete') or frame.get('type') == 'done':
                if ''.join(chunks).strip():
                    return ''.join(chunks)
                raise RuntimeError('已结束但没有文本回复')


def main():
    args = parse_args()
    print(f'会话 ID：{args.session_id}', flush=True)
    if args.dry_run:
        print('离线参数检查通过；未调用云端。')
        return 0
    key = os.getenv('AGENTARTS_API_KEY', '').strip()
    if not key or '\n' in key or '\r' in key:
        print('请设置 AGENTARTS_API_KEY，只填密钥本身，不加 Bearer。', file=sys.stderr)
        return 2
    start = time.monotonic()
    try:
        reply = asyncio.run(asyncio.wait_for(exchange(args, key), args.timeout))
    except TimeoutError:
        print('调用超时，未判定通过。', file=sys.stderr)
        return 1
    except Exception as exc:
        # 不输出第三方异常内容，避免其中包含鉴权或完整握手信息。
        detail = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        print(f'调用未通过：{detail.replace(key, "[已隐藏]")}', file=sys.stderr)
        return 1
    print(f'回复：\n{reply.replace(key, "[已隐藏]")}')
    print(f'连通测试通过，用时 {time.monotonic() - start:.1f} 秒；回答质量尚需人工检查。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
