"""Persistent CDP bridge daemon.

Chrome 144+ asks "Allow remote debugging?" once per WebSocket connection.
Keeping ONE long-lived connection therefore costs the user a single click for
the whole session. This daemon holds that connection and serves tiny JSON
requests over 127.0.0.1:9333.

Protocol: one JSON object per line, response one JSON object per line.
Ops:
  {"op":"ping"}
  {"op":"targets"}
  {"op":"open","url":"..."}            -> {targetId, sessionId}
  {"op":"attach","targetId":"..."}     -> {sessionId}
  {"op":"eval","sessionId":"...","expression":"..."} -> {value}
  {"op":"call","method":"...","params":{},"sessionId":"..."} -> {result}
  {"op":"text","sessionId":"...","selector":"body"} -> {text}
  {"op":"html","sessionId":"..."}      -> {html}
  {"op":"close","targetId":"..."}
  {"op":"shutdown"}
"""
import json
import os
import socketserver
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp_browser import CDP  # noqa: E402

WS = os.environ.get("CDP_WS", "ws://127.0.0.1:9222/devtools/browser")
PORT = int(os.environ.get("CDP_PORT", "9333"))
LOG = "/tmp/cdp_daemon.log"

_state = {"cdp": None, "sessions": {}}
# Chrome CDP multiplexes replies on one socket: concurrent callers would read
# each other's frames and desync the stream permanently.
_LOCK = threading.Lock()


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ensure():
    cdp = _state["cdp"]
    if cdp is None:
        cdp = CDP(WS, timeout=120)
        _state["cdp"] = cdp
        _state["sessions"] = {}
        log("cdp connected")
    return cdp


def reset_cdp():
    cdp = _state.get("cdp")
    if cdp is not None:
        try:
            cdp.close()
        except Exception:
            pass
    _state["cdp"] = None
    _state["sessions"] = {}


def handle(req):
    """Dispatch one request, reconnecting once if the CDP socket died."""
    try:
        return dispatch(req)
    except (BrokenPipeError, ConnectionError, OSError) as e:
        log(f"cdp socket lost ({type(e).__name__}), reconnecting")
        reset_cdp()
        cdp = ensure()          # new WS handshake = one more "allow" click
        cdp.call("Target.getTargets")
        return dispatch(req)


def dispatch(req):
    cdp = ensure()
    op = req.get("op", "call")
    if op == "ping":
        return {"ok": True, "pid": os.getpid()}
    if op == "targets":
        return {"ok": True, "targets": cdp.call("Target.getTargets")["targetInfos"]}
    if op == "open":
        r = cdp.call("Target.createTarget", {"url": req.get("url", "about:blank")})
        tid = r["targetId"]
        # Attaching before the first navigation settles can drop the target.
        time.sleep(1.5)
        sess = cdp.call(
            "Target.attachToTarget", {"targetId": tid, "flatten": True}
        )["sessionId"]
        cdp.call("Page.enable", session_id=sess)
        cdp.call("Runtime.enable", session_id=sess)
        _state["sessions"][tid] = sess
        return {"ok": True, "targetId": tid, "sessionId": sess}
    if op == "attach":
        tid = req["targetId"]
        if tid in _state["sessions"]:
            return {"ok": True, "sessionId": _state["sessions"][tid]}
        sess = cdp.call(
            "Target.attachToTarget", {"targetId": tid, "flatten": True}
        )["sessionId"]
        _state["sessions"][tid] = sess
        return {"ok": True, "sessionId": sess}
    if op == "eval":
        value = cdp.eval_js(
            req["sessionId"],
            req["expression"],
            await_promise=bool(req.get("awaitPromise")),
        )
        return {"ok": True, "value": value}
    if op == "text":
        return {
            "ok": True,
            "text": cdp.text(
                req["sessionId"], req.get("selector", "body"), req.get("limit", 200000)
            ),
        }
    if op == "html":
        return {"ok": True, "html": cdp.html(req["sessionId"], req.get("limit", 500000))}
    if op == "call":
        return {
            "ok": True,
            "result": cdp.call(
                req["method"], req.get("params"), session_id=req.get("sessionId")
            ),
        }
    if op == "close":
        cdp.close_tab(req["targetId"])
        _state["sessions"].pop(req["targetId"], None)
        return {"ok": True}
    if op == "shutdown":
        threading.Thread(target=lambda: (time.sleep(0.3), os._exit(0)), daemon=True).start()
        return {"ok": True, "bye": True}
    return {"ok": False, "error": f"unknown op {op}"}


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for raw in self.rfile:
            raw = raw.strip()
            if not raw:
                continue
            try:
                req = json.loads(raw)
                with _LOCK:
                    resp = handle(req)
            except Exception as e:  # noqa: BLE001
                resp = {"ok": False, "error": f"{type(e).__name__}: {e}"}
            self.wfile.write((json.dumps(resp, ensure_ascii=False) + "\n").encode())
            self.wfile.flush()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    log(f"starting daemon pid={os.getpid()} ws={WS} port={PORT}")
    ensure()
    srv = Server(("127.0.0.1", PORT), Handler)
    log(f"listening on 127.0.0.1:{PORT}")
    srv.serve_forever()
