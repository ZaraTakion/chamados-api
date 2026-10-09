"""Public, credential-free smoke checks for a deployed Chamados API.

Usage: python scripts/smoke_deploy.py https://your-public-api.example.com
Local only: python scripts/smoke_deploy.py http://127.0.0.1:8000 --allow-http-local
"""

import argparse
import json
import re
import urllib.request
from urllib.parse import urlsplit

HEALTH_PATHS = ("/api/health/live/", "/api/health/ready/")
PUBLIC_PATHS = ("/api/schema/", "/api/docs/")
_REQUEST_ID_RE = re.compile(r"^[0-9a-f]{32}$")


def validate_base_url(base_url, allow_http_local=False):
    parsed = urlsplit(base_url)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Use an origin URL without credentials, query, or fragment")
    if parsed.path not in ("", "/"):
        raise ValueError("Supply only the base origin, without an endpoint path")
    if parsed.scheme == "https" and parsed.hostname:
        return base_url.rstrip("/")
    if (
        parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        and allow_http_local
    ):
        return base_url.rstrip("/")
    raise ValueError("Public smoke tests require an HTTPS origin; local HTTP requires explicit opt-in")


def check_deployment(base_url, *, allow_http_local=False):
    origin = validate_base_url(base_url, allow_http_local=allow_http_local)
    for path in HEALTH_PATHS + PUBLIC_PATHS:
        request = urllib.request.Request(
            origin + path,
            headers={"User-Agent": "chamados-api-deploy-smoke/1"},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=12) as response:
            if response.status != 200:
                raise AssertionError(f"{path}: expected HTTP 200, got {response.status}")
            final_url = urlsplit(response.geturl())
            if urlsplit(origin).scheme == "https" and final_url.scheme != "https":
                raise AssertionError(f"{path}: refused HTTPS downgrade")
            if path in HEALTH_PATHS:
                data = json.loads(response.read())
                if data.get("status") != "ok" or "timestamp" not in data:
                    raise AssertionError(f"{path}: invalid health payload")
                if "no-store" not in response.headers.get("Cache-Control", ""):
                    raise AssertionError(f"{path}: missing Cache-Control: no-store")
                if not _REQUEST_ID_RE.fullmatch(response.headers.get("X-Request-ID", "")):
                    raise AssertionError(f"{path}: missing valid request ID")
        print(f"PASS {path}")


def main():
    parser = argparse.ArgumentParser(description="Verify a deployed Chamados API via public GET routes.")
    parser.add_argument("base_url", help="HTTPS origin (no path, secrets, or tokens)")
    parser.add_argument("--allow-http-local", action="store_true", help="Allow HTTP for localhost only")
    args = parser.parse_args()
    check_deployment(args.base_url, allow_http_local=args.allow_http_local)
    print("Smoke checks passed. This does NOT verify worker, database backups, or authenticated flows.")


if __name__ == "__main__":
    main()
