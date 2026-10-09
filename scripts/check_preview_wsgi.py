"""Verify protected-preview WSGI HTTP behavior on loopback without Cloudflare.

CI-only: no public endpoint, demo credentials, or remote network calls.
"""

import http.client
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from scripts.protected_preview import preview_environment

ROOT = Path(__file__).resolve().parents[1]


def request(port, host, secure, path="/api/health/live/"):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    headers = {"Host": host}
    if secure:
        headers["X-Forwarded-Proto"] = "https"
    try:
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    host = "ci-proof.trycloudflare.com"
    env = preview_environment(os.environ, host)
    env["PROTECTED_PREVIEW_PORT"] = str(port)
    db_path = ROOT / "data" / "protected-preview.sqlite3"
    db_path.parent.mkdir(exist_ok=True)

    subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        cwd=ROOT, env=env, check=True,
    )
    server = subprocess.Popen(
        [sys.executable, "-c", "from scripts.protected_preview import serve_wsgi; serve_wsgi()"],
        cwd=ROOT, env=env,
    )
    try:
        for _ in range(60):
            if server.poll() is not None:
                raise RuntimeError("Waitress exited before loopback smoke test.")
            try:
                code, _, _ = request(port, host, True)
                if code == 200:
                    break
            except OSError:
                pass
            time.sleep(0.1)
        else:
            raise RuntimeError("Waitress did not become ready on loopback.")

        code, _, data = request(port, host, True)
        assert code == 200 and b'"status":"ok"' in data.replace(b" ", b""), (code, data[:120])
        code, headers, _ = request(port, host, False, "/api/auth/me/")
        assert code == 301, code
        assert headers["Location"] == f"https://{host}/api/auth/me/", headers
        code, _, _ = request(port, "malicious.example.com", True)
        assert code == 400, code
        print("Protected preview loopback WSGI smoke PASSED: HTTPS, redirect and strict Host.")
    finally:
        server.terminate()
        try:
            server.wait(timeout=8)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
        for path in (db_path, Path(str(db_path) + "-shm"), Path(str(db_path) + "-wal"), Path(str(db_path) + "-journal")):
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
