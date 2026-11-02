"""Shared helper: talk to the persistent CDP daemon on 127.0.0.1:9333."""
import json
import socket

PORT = 9333


def request(req, timeout=180):
    s = socket.create_connection(("127.0.0.1", PORT), timeout=timeout)
    s.sendall((json.dumps(req, ensure_ascii=False) + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = s.recv(1 << 16)
        if not chunk:
            break
        buf += chunk
    s.close()
    return json.loads(buf.decode("utf-8", "replace"))


def open_tab(url, wait=4.0):
    """Create a tab already pointing at url, then attach.

    Attaching before the first navigation finishes can make Chrome drop the
    target, so create with the URL and attach a moment later.
    """
    import time

    r = request({"op": "call", "method": "Target.createTarget", "params": {"url": url}})
    if not r.get("ok"):
        raise RuntimeError(r)
    tid = r["result"]["targetId"]
    time.sleep(1.5)
    a = request({"op": "attach", "targetId": tid})
    if not a.get("ok"):
        time.sleep(2)
        a = request({"op": "attach", "targetId": tid})
    if not a.get("ok"):
        raise RuntimeError(a)
    time.sleep(max(0.0, wait - 1.5))
    return tid, a["sessionId"]


def close_tab(target_id):
    request({"op": "close", "targetId": target_id})


def eval_js(session_id, expression, await_promise=False):
    r = request(
        {"op": "eval", "sessionId": session_id, "expression": expression,
         "awaitPromise": await_promise}
    )
    if not r.get("ok"):
        raise RuntimeError(r)
    return r["value"]


def text(session_id, selector="body", limit=200000):
    r = request({"op": "text", "sessionId": session_id, "selector": selector, "limit": limit})
    if not r.get("ok"):
        raise RuntimeError(r)
    return r["text"]


def html(session_id, limit=500000):
    r = request({"op": "html", "sessionId": session_id, "limit": limit})
    if not r.get("ok"):
        raise RuntimeError(r)
    return r["html"]
