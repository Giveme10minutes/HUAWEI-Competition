"""Minimal Chrome DevTools Protocol client (stdlib only).

Connects to the user's running Chrome via ws://127.0.0.1:9222/devtools/browser
and exposes a few helpers for tab creation, navigation and JS evaluation.

Usage:
    python3 -I scripts/cdp_browser.py <url>   # smoke test: open url, dump title+text
"""
import base64
import itertools
import json
import os
import socket
import struct
import time
import urllib.parse


class CDPError(RuntimeError):
    pass


class CDP:
    def __init__(self, ws_url="ws://127.0.0.1:9222/devtools/browser", timeout=30):
        u = urllib.parse.urlparse(ws_url)
        self.host = u.hostname
        self.port = u.port or 80
        self.path = u.path or "/"
        self.timeout = timeout
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        self.sock.sendall(req.encode())
        resp = self._read_http_headers()
        if b"101" not in resp.split(b"\r\n", 1)[0]:
            raise CDPError(f"websocket handshake failed: {resp[:200]!r}")
        self._ids = itertools.count(1)
        self._buf = b""

    # ---------------- low level ----------------

    def _read_http_headers(self):
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            data += chunk
        head, _, rest = data.partition(b"\r\n\r\n")
        self._buf = rest
        return head

    def _send_frame(self, payload, opcode=1):
        data = payload.encode() if isinstance(payload, str) else payload
        header = bytearray([0x80 | opcode])
        n = len(data)
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", n)
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.sock.sendall(bytes(header) + masked)

    def _read_frame(self):
        buf = self._buf
        while len(buf) < 2:
            buf += self._recv_some()
        b1, b2 = buf[0], buf[1]
        opcode = b1 & 0x0F
        masked = b2 & 0x80
        n = b2 & 0x7F
        offset = 2
        if n == 126:
            while len(buf) < 4:
                buf += self._recv_some()
            n = struct.unpack(">H", buf[2:4])[0]
            offset = 4
        elif n == 127:
            while len(buf) < 10:
                buf += self._recv_some()
            n = struct.unpack(">Q", buf[2:10])[0]
            offset = 10
        if masked:
            while len(buf) < offset + 4:
                buf += self._recv_some()
            mask = buf[offset:offset + 4]
            offset += 4
        while len(buf) < offset + n:
            buf += self._recv_some()
        payload = buf[offset:offset + n]
        if masked:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._buf = buf[offset + n:]
        return opcode, payload

    def _recv_some(self):
        chunk = self.sock.recv(65536)
        if not chunk:
            raise CDPError("socket closed")
        return chunk

    def _recv_message(self):
        opcode, payload = self._read_frame()
        # reassemble fragmented text messages
        while opcode == 0:  # continuation
            opcode2, more = self._read_frame()
            payload += more
            opcode = 1 if opcode2 == 1 else opcode2
        if opcode == 8:
            raise CDPError("websocket closed by peer")
        return json.loads(payload.decode("utf-8", "replace"))

    def call(self, method, params=None, session_id=None, timeout=None):
        mid = next(self._ids)
        msg = {"id": mid, "method": method, "params": params or {}}
        if session_id:
            msg["sessionId"] = session_id
        self._send_frame(json.dumps(msg, ensure_ascii=False))
        deadline = time.time() + (timeout or self.timeout)
        while True:
            if time.time() > deadline:
                raise CDPError(f"timeout waiting for {method}")
            self.sock.settimeout(max(0.2, deadline - time.time()))
            m = self._recv_message()
            if m.get("id") == mid:
                if "error" in m:
                    raise CDPError(f"{method} -> {m['error']}")
                return m.get("result", {})
            # ignore events

    # ---------------- helpers ----------------

    def new_tab(self, url="about:blank"):
        r = self.call("Target.createTarget", {"url": url})
        return r["targetId"]

    def attach(self, target_id):
        r = self.call("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        sid = r["sessionId"]
        self.call("Page.enable", session_id=sid)
        self.call("Runtime.enable", session_id=sid)
        return sid

    def eval_js(self, sid, expression, await_promise=False):
        r = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
                "userGesture": True,
            },
            session_id=sid,
        )
        if "exceptionDetails" in r:
            return {"__error__": str(r["exceptionDetails"].get("exception", {}).get("description"))}
        return r.get("result", {}).get("value")

    def navigate(self, sid, url, wait_dom=True, timeout=25):
        self.call("Page.navigate", {"url": url}, session_id=sid)
        if wait_dom:
            self.wait_ready(sid, timeout)

    def wait_ready(self, sid, timeout=25):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                state = self.eval_js(sid, "document.readyState")
            except CDPError:
                state = None
            if state == "complete":
                return True
            time.sleep(0.4)
        return False

    def text(self, sid, selector="body", limit=200000):
        expr = (
            "(() => { const el = document.querySelector(%r); return el ? el.innerText : ''; })()"
            % selector
        )
        return (self.eval_js(sid, expr) or "")[:limit]

    def html(self, sid, limit=500000):
        return (self.eval_js(sid, "document.documentElement.outerHTML") or "")[:limit]

    def url(self, sid):
        return self.eval_js(sid, "location.href")

    def close_tab(self, target_id):
        try:
            self.call("Target.closeTarget", {"targetId": target_id})
        except CDPError:
            pass

    def close(self):
        try:
            self._send_frame(b"", opcode=8)
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass


def smoke(url):
    b = CDP()
    tid = b.new_tab(url)
    sid = b.attach(tid)
    b.wait_ready(sid)
    print("TITLE:", b.eval_js(sid, "document.title"))
    print("URL:", b.url(sid))
    print("TEXT:", b.text(sid)[:500])
    b.close_tab(tid)
    b.close()


if __name__ == "__main__":
    import sys

    smoke(sys.argv[1] if len(sys.argv) > 1 else "https://example.com")
