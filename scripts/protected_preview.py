"""Launch an email-protected, temporary Cloudflare Quick Tunnel for the demo.

No account, paid service or production deployment is created.
Requires cloudflared >= 2026.9.3 and a trusted email address.

Run in CMD: python scripts/protected_preview.py --allowed-mail you@example.com
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com\b")
VERSION_RE = re.compile(r"\b(\d{4})\.(\d+)\.(\d+)\b")
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_\x60{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_email(email):
    if not EMAIL_RE.fullmatch(email) or len(email) > 254 or "*" in email:
        raise ValueError("Informe um email especifico, sem curingas.")
    return email


def check_cloudflared_version(output):
    match = VERSION_RE.search(output)
    if not match or tuple(map(int, match.groups())) < (2026, 9, 3):
        raise ValueError("O preview protegido exige cloudflared 2026.9.3 ou superior.")


def preview_environment(source, host):
    """Isolate data and turn off DEBUG; do not reuse development credentials."""
    from django.core.management.utils import get_random_secret_key

    if not re.fullmatch(r"[a-z0-9-]+\.trycloudflare\.com", host):
        raise ValueError("Hostname Quick Tunnel invalido.")
    result = dict(source)
    result.pop("DATABASE_URL", None)
    result["DJANGO_PROTECTED_PREVIEW"] = "true"
    result["DJANGO_DEBUG"] = "false"
    result["DJANGO_SECRET_KEY"] = get_random_secret_key() + get_random_secret_key()
    result["DJANGO_ALLOWED_HOSTS"] = host
    result["DJANGO_SECURE_SSL_REDIRECT"] = "true"
    result["DJANGO_TRUST_PROXY_SSL_HEADER"] = "false"
    result["DJANGO_HSTS_SECONDS"] = "0"
    result["SQLITE_PATH"] = str(ROOT / "data" / "protected-preview.sqlite3")
    result["DJANGO_SETTINGS_MODULE"] = "chamados_api.settings"
    return result


def start_cloudflared(binary, emails, port):
    command = [
        binary, "tunnel", "--url", f"http://127.0.0.1:{port}",
    ]
    for email in emails:
        command.extend(["--allowed-mail", email])
    proc = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    return proc


def await_tunnel_url(proc):
    """Never start the API until a Cloudflare protected link was obtained."""
    for line in proc.stdout:
        match = URL_RE.search(line)
        if match:
            return match.group(0)
        if proc.poll() is not None:
            break
    raise RuntimeError("cloudflared nao produziu URL. Verifique rede e versao.")


def run_command(args, env):
    subprocess.run([sys.executable, *args], cwd=ROOT, env=env, check=True)


def serve_wsgi():
    """Waitress validates scheme headers only from the local proxy."""
    from waitress import serve
    from chamados_api.wsgi import application

    serve(
        application,
        host="127.0.0.1",
        port=int(os.environ["PROTECTED_PREVIEW_PORT"]),
        threads=2,
        trusted_proxy="127.0.0.1",
        trusted_proxy_headers={"x-forwarded-proto"},
        clear_untrusted_proxy_headers=True,
    )


def stop_process(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(
        description="Demonstração privada e gratuita via Cloudflare Quick Tunnel.",
    )
    parser.add_argument(
        "--allowed-mail", action="append", required=True,
        help="Email autorizado a receber PIN. Pode repetir para mais de uma pessoa.",
    )
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        emails = list(dict.fromkeys(validate_email(x) for x in args.allowed_mail))
        if not 1 <= len(emails) <= 3:
            raise ValueError("Permita entre 1 e 3 enderecos de email individuais.")
        if not 1024 <= args.port <= 65535:
            raise ValueError("Porta local invalida.")
    except ValueError as exc:
        parser.error(str(exc))

    binary = shutil.which("cloudflared")
    if not binary:
        parser.error("cloudflared nao instalado. Consulte docs/PROTECTED_TUNNEL.md.")
    version = subprocess.run(
        [binary, "--version"], capture_output=True, text=True, check=True,
    )
    try:
        check_cloudflared_version(version.stdout + version.stderr)
    except ValueError as exc:
        parser.error(str(exc))

    tunnel = server = notifier = None
    try:
        tunnel = start_cloudflared(binary, emails, args.port)
        url = await_tunnel_url(tunnel)
        hostname = urlsplit(url).hostname
        env = preview_environment(os.environ, hostname)
        env["PROTECTED_PREVIEW_PORT"] = str(args.port)

        # The database is intentionally isolated from data/db.sqlite3.
        (ROOT / "data").mkdir(exist_ok=True)
        run_command(["manage.py", "migrate", "--noinput"], env)
        run_command(["manage.py", "collectstatic", "--noinput"], env)
        run_command(["manage.py", "check", "--deploy"], env)

        server = subprocess.Popen(
            [sys.executable, "-c", "from scripts.protected_preview import serve_wsgi; serve_wsgi()"],
            cwd=ROOT, env=env,
        )
        notifier = subprocess.Popen(
            [sys.executable, "manage.py", "process_notifications", "--watch", "--interval", "10"],
            cwd=ROOT, env=env,
        )
        print("Swagger privado:", url + "/api/docs/", flush=True)
        print("Somente emails autorizados recebem o PIN de acesso.", flush=True)
        print("Banco isolado: data/protected-preview.sqlite3 (nenhum dado do SQLite atual).", flush=True)
        print("Use Ctrl+C para ENCERRAR o tunnel, o servidor e o processador.", flush=True)
        while True:
            if any(p.poll() is not None for p in (tunnel, server, notifier)):
                raise RuntimeError("Um dos processos encerrou. Fechando todos para evitar preview parcial.")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Preview encerrado.", flush=True)
    finally:
        for proc in (notifier, server, tunnel):
            stop_process(proc)


if __name__ == "__main__":
    main()
