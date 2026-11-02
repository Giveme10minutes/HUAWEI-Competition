"""Tiny client for the persistent CDP daemon (127.0.0.1:9333).

Usage:
  python3 -I scripts/cdp_cli.py '{"op":"ping"}'
  python3 -I scripts/cdp_cli.py --file req.json
  echo '{"op":"targets"}' | python3 -I scripts/cdp_cli.py

Prints the daemon's JSON reply. Exit code 1 when ok=false.
"""
import json
import socket
import sys

PORT = 9333


def main(argv):
    if len(argv) > 1 and argv[1] == "--file":
        raw = open(argv[2], encoding="utf-8").read()
    elif len(argv) > 1:
        raw = argv[1]
    else:
        raw = sys.stdin.read()
    req = json.loads(raw)
    s = socket.create_connection(("127.0.0.1", PORT), timeout=180)
    s.sendall((json.dumps(req, ensure_ascii=False) + "\n").encode())
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = s.recv(1 << 16)
        if not chunk:
            break
        buf += chunk
    s.close()
    resp = json.loads(buf.decode("utf-8", "replace"))
    out = json.dumps(resp, ensure_ascii=False)
    if req.get("op") in ("text", "html") and len(out) < 5000:
        print(out)
    else:
        print(out[:20000])
    if not resp.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
